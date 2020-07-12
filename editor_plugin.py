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

DEFAULT_COMMAND = 'gvim --remote-silent +{line} {filepath}'
DEFAULT_REGEX = r'([^ \t\n\r\f\v:]+?):([0-9]+)'
DEFAULT_GROUPS = 'file line'
DEFAULT_OPEN_IN_CURRENT_TERM = False

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
        }
        saved_config = self.config.plugin_get_config(self.plugin_name)
        if saved_config is not None:
            config.update(saved_config)
        config["open_in_current_term"] = to_bool(config["open_in_current_term"])
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

    def search_filepath_in_libdir(self, group_value):
        filename = group_value.split('/')[-1]
        libdir = self.config.plugin_get(self.plugin_name, 'libdir')

        for dirpath, dirnames, filenames in os.walk(os.path.expanduser(libdir)):
            for name in filenames:
                if name == filename:
                    return os.path.join(dirpath, name)

    def get_filepath(self, strmatch):
        filepath = None
        line = column = '1'

        config = self.config.plugin_get_config(self.plugin_name)
        match = re.match(config['match'], strmatch)
        groups = [group for group in match.groups() if group is not None]
        group_names = config['groups'].split()

        for group_value, group_name in zip(groups, group_names):
            if group_name == 'file':
                filepath = os.path.join(self.get_cwd(), group_value)
                if not os.path.exists(filepath):
                    filepath = self.search_filepath_in_libdir(group_value)
            elif group_name == 'line':
                line = group_value
            elif group_name == 'column':
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
                    self.get_terminal().feed(command + '\n')
                else:
                    subprocess.call(shlex.split(command))
                return '--version'
            return command
