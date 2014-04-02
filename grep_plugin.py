"""
Terminator plugin to open grep output using a chosen editor. 
Currently supports gvim and gedit.

Author: michele.silva@gmail.com
License: GPLv2
"""
import inspect, os, shlex, subprocess
from terminatorlib import plugin
from terminatorlib import config

AVAILABLE = ['GrepPlugin']
DEFAULT_COMMAND = 'gvim --remote-silent {filepath} +{line}'


class GrepPlugin(plugin.URLHandler):
    """ Process URLs returned by the grep command. """
    capabilities = ['url_handler']
    handler_name = 'grepurl'
    nameopen = "Open File"
    namecopy = "Copy Open Command"
    match = '[^ \t\n\r\f\v]+?[:]([0-9]+?[:])+'

    def __init__(self):
       self.plugin_name = self.__class__.__name__
       self.current_path = None
       self.config = config.Config()
       current_config = self.config.plugin_get_config(self.plugin_name)
       # Setup default options
       if not current_config:
          self.config.plugin_set(self.plugin_name, 'command', DEFAULT_COMMAND)
          self.config.save()

    def get_current_path(self):
        """ HACK 1: Use inspect to get the Terminal object and get_cwd(). """
        for frameinfo in inspect.stack():
            frameobj = frameinfo[0].f_locals.get('self')
            if frameobj and frameobj.__class__.__name__ == 'Terminal':
                return frameobj.get_cwd()
        return None

    def is_called_by_open(self):
        """ HACK 2: Use inspect to check we are called via open_url(). """
        for frameinfo in inspect.stack():
            if frameinfo[3] == 'open_url':
                return True
        return False

    def callback(self, filepath):
        # Cleanup the Filepath
        filepath = filepath[:-1]
        if ':' in filepath:
            filepath,line = filepath.split(':')
        current_path = self.get_current_path()
        if current_path:
            filepath = os.path.join(current_path, filepath)
        # Generate the openurl string
        command = self.config.plugin_get(self.plugin_name, 'command')
        command = command.replace('{filepath}', filepath)
        command = command.replace('{line}', line)
        # Check we are opening the file
        if self.is_called_by_open():
            subprocess.call(shlex.split(command))
            return '--version'
        return command
