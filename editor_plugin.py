"""
Terminator plugin to open a file using a chosen editor.

Author: michele.silva@gmail.com
License: GPLv2
Site: https://github.com/mchelem/terminator-editor-plugin
"""
import inspect
import os
import re
import shlex
import subprocess
from terminatorlib import plugin, config

AVAILABLE = ['EditorPlugin']

# Global state to track git diff context
_git_diff_context = {'file': None, 'line': None}

DEFAULT_COMMAND = 'gvim --remote-silent +{line} {filepath}'
# Basic regex for file paths with line numbers (used when git_diff_support is disabled)
DEFAULT_REGEX = r'(?:^|(?<= ))(?![ab]/)([a-zA-Z0-9_/.\-]+\.[a-zA-Z0-9]+)(:[0-9]+)?(:[0-9]+)?(?=$|[ \t])'
# Extended regex including git diff patterns (used when git_diff_support is enabled)
GIT_DIFF_REGEX = r'(?<=--- a/)[^ \t\n]+|(?<=\+\+\+ b/)[^ \t\n]+|(?<=diff --git a/)[^ \t\n]+|@@ [^@]+ @@|' + DEFAULT_REGEX
DEFAULT_GROUPS = 'file line column'
DEFAULT_OPEN_IN_CURRENT_TERM = False
DEFAULT_GIT_DIFF_SUPPORT = True

def to_bool(val):
    return val == "True"

class EditorPlugin(plugin.URLHandler):
    """ Process URLs returned by commands. """
    capabilities = ['url_handler']
    handler_name = 'editorurl'
    nameopen = 'Open File'
    namecopy = 'Copy Open Command'

    def __init__(self):
        self.plugin_name = self.__class__.__name__
        self.config = config.Config()
        self.check_config()
        self.match = self.config.plugin_get(self.plugin_name, 'match')
        if hasattr(self.match, 'decode'):
            self.match = self.match.decode('string_escape')

    def check_config(self):
        config = {
            'command': DEFAULT_COMMAND,
            'match': DEFAULT_REGEX,
            'groups': DEFAULT_GROUPS,
            'open_in_current_term': DEFAULT_OPEN_IN_CURRENT_TERM,
            'git_diff_support': DEFAULT_GIT_DIFF_SUPPORT,
        }
        saved_config = self.config.plugin_get_config(self.plugin_name)
        if saved_config is not None:
            config.update(saved_config)
        config["open_in_current_term"] = to_bool(config["open_in_current_term"])
        config["git_diff_support"] = to_bool(config.get("git_diff_support", DEFAULT_GIT_DIFF_SUPPORT))
        
        # Update regex based on git_diff_support setting
        if config["git_diff_support"]:
            config['match'] = GIT_DIFF_REGEX
        
        self.config.plugin_set_config(self.plugin_name, config)
        self.config.save()

    def get_terminal(self):
        # HACK: Because the current working directory is not available to
        # plugins, we need to use the inspect module to climb up the stack to
        # the Terminal object and call get_cwd() from there.
        for frameinfo in inspect.stack():
            frameobj = frameinfo[0].f_locals.get('self')
            if frameobj and frameobj.__class__.__name__ == 'Terminal':
                return frameobj

    def get_cwd(self):
        """ Return current working directory. """
        term = self.get_terminal()
        if term:
            return term.get_cwd()

    def open_url(self):
        """ Return True if we should open the file. """
        # HACK: Because the plugin doesn't tell us we should open or copy
        # the command, we need to climb the stack to see how we got here.
        return inspect.stack()[3][3] == 'open_url'

    def update_git_diff_context(self, strmatch):
        """ Update global context when we see git diff headers or hunk markers """
        global _git_diff_context

        # Check if this is a filename match (from lookbehind patterns)
        # These won't have the --- or +++ prefix since lookbehind excludes them
        # We identify them by checking if they look like file paths (contain / or .)
        if ('/' in strmatch or '.' in strmatch) and not strmatch.startswith('@@'):
            # This is likely a file path from git diff header
            _git_diff_context['file'] = strmatch
            _git_diff_context['line'] = None
            return

        # Check for hunk header: @@ -71,7 +71,7 @@
        hunk_match = re.search(r'@@ -\d+,?\d* \+(\d+)', strmatch)
        if hunk_match:
            _git_diff_context['line'] = hunk_match.group(1)
            return

    def search_filepath_in_libdir(self, group_value):
        filename = group_value.split('/')[-1]
        libdir = self.config.plugin_get(self.plugin_name, 'libdir')

        for dirpath, dirnames, filenames in os.walk(os.path.expanduser(libdir)):
            for name in filenames:
                if name == filename:
                    return os.path.join(dirpath, name)

    def get_filepath(self, strmatch):
        global _git_diff_context
        filepath = None
        line = column = '1'

        config = self.config.plugin_get_config(self.plugin_name)
        git_diff_enabled = config.get('git_diff_support', DEFAULT_GIT_DIFF_SUPPORT)
        
        # Git diff processing (only if enabled)
        if git_diff_enabled:
            # Always update context for git diff tracking
            self.update_git_diff_context(strmatch)

            # Special handling for git diff hunk headers (@@ -x,y +a,b @@)
            # Make these clickable using the cached file from previous --- or +++ line
            if strmatch.startswith('@@'):
                hunk_match = re.search(r'@@ -\d+,?\d* \+(\d+)', strmatch)
                if hunk_match and _git_diff_context.get('file'):
                    filepath = os.path.join(self.get_cwd(), _git_diff_context['file'])
                    line = hunk_match.group(1)
                    return filepath, line, column
            
            # Special handling for git diff file headers (matched via lookbehind)
            # strmatch will be just the filename (e.g., "app-be/composer.json")
            elif ('/' in strmatch or '.' in strmatch):
                filepath = os.path.join(self.get_cwd(), strmatch)
                # Use cached line number if available from previous @@ header
                if _git_diff_context.get('line'):
                    line = _git_diff_context['line']
                return filepath, line, column

        config = self.config.plugin_get_config(self.plugin_name)
        match = re.match(config['match'], strmatch)
        if not match:
            return filepath, line, column

        groups = match.groups()
        group_names = config['groups'].split()

        for group_value, group_name in zip(groups, group_names):
            if group_value is None:
                continue
            # Clean up colon prefix from line/column groups
            if group_value.startswith(':'):
                group_value = group_value[1:]

            if group_name == 'file':
                # Try absolute path first
                if os.path.isabs(group_value) and os.path.exists(group_value):
                    filepath = group_value
                # Try relative to cwd
                else:
                    filepath = os.path.join(self.get_cwd(), group_value)
                    if not os.path.exists(filepath):
                        filepath = self.search_filepath_in_libdir(group_value)
            elif group_name == 'line' and group_value:
                line = group_value
            elif group_name == 'column' and group_value:
                column = group_value
        return filepath, line, column

    def callback(self, strmatch):
        filepath, line, column = self.get_filepath(strmatch)
        if filepath:
            command = self.config.plugin_get(self.plugin_name, 'command')
            command = command.replace('{filepath}', filepath)
            command = command.replace('{line}', line)
            command = command.replace('{column}', column)
            if self.open_url():
                if self.config.plugin_get(self.plugin_name, 'open_in_current_term'):
                    self.get_terminal().vte.feed_child((command+'\n').encode())
                else:
                    subprocess.Popen(shlex.split(command))
                return '--version'
            return command
