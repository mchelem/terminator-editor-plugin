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
        self.match = self.match.decode('string_escape')

    def check_config(self):
        config = {
            'command': DEFAULT_COMMAND,
            'match': DEFAULT_REGEX,
        }
        saved_config = self.config.plugin_get_config(self.plugin_name)
        config.update(saved_config)
        self.config.plugin_set_config(self.plugin_name, config)
        self.config.save()

    def get_cwd(self):
        """ Return current working directory. """
        # HACK: Because the current working directory is not available to
        # plugins, we need to use the inspect module to climb up the stack to
        # the Terminal object and call get_cwd() from there.
        for frameinfo in inspect.stack():
            frameobj = frameinfo[0].f_locals.get('self')
            if frameobj and frameobj.__class__.__name__ == 'Terminal':
                return frameobj.get_cwd()
        return None

    def open_url(self):
        """ Return True if we should open the file. """
        # HACK: Because the plugin doesn't tell us we should open or copy
        # the command, we need to climb the stack to see how we got here.
        return inspect.stack()[3][3] == 'open_url'

    def get_filepath(self, strmatch):
        config = self.config.plugin_get_config(self.plugin_name)
        match = re.match(config['match'], strmatch)
        groups = [group for group in match.groups() if group is not None]
        lineno = '1'
        filepath = None
        # Iterate through match groups in order to find file and lineno if any
        for item in groups:
            fileitem = os.path.join(self.get_cwd(), item)
            if os.path.exists(fileitem):
                filepath = fileitem
                continue
            try:
                int(item)
            except ValueError:
                pass
            else:
                lineno = item
        return filepath, lineno

    def callback(self, strmatch):
        filepath, lineno = self.get_filepath(strmatch)
        # Generate the openurl string
        command = self.config.plugin_get(self.plugin_name, 'command')
        command = command.replace('{filepath}', filepath)
        command = command.replace('{line}', lineno)
        # Check we are opening the file
        if self.open_url():
            if filepath:
                subprocess.call(shlex.split(command))
            return '--version'
        return command
