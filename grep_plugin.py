"""
Terminator plugin to open grep output using a chosen editor. 
Currently supports gvim and gedit.

Author: michele.silva@gmail.com
License: GPL v2
"""
import inspect, os, shlex, subprocess
from terminatorlib import plugin
from terminatorlib import config

AVAILABLE = ['GrepPlugin']
DEFAULT_EDITOR = 'gvim'
DEFAULT_OPENURL = '{editor} --remote-silent {filepath} +{line}'


class GrepPlugin(plugin.URLHandler):
    """ Process URLs returned by the grep command. """
    capabilities = ['url_handler']
    handler_name = 'grepurl'
    nameopen = "Open in editor"
    namecopy = "Copy editor URL"
    match = '[^ \t\n\r\f\v]+?[:]([0-9]+?[:])+'

    def __init__(self):
       self.plugin_name = self.__class__.__name__
       self.current_path = None
       self.config = config.Config()
       current_config = self.config.plugin_get_config(self.plugin_name)
       # Setup default options
       if not current_config:
          self.config.plugin_set(self.plugin_name, 'editor', DEFAULT_EDITOR)
          self.config.plugin_set(self.plugin_name, 'openurl', DEFAULT_OPENURL)
          self.config.save()

    def is_called_by_open(self):
        """ A hack to check if it is being called by the open_url function. """
        # open_url(3) -> prepare_url(2) -> callback(1)
        return inspect.stack()[3][3] == "open_url"
    
    def callback(self, filepath):
        # Cleanup the Filepath
        filepath = filepath[:-1]
        if ':' in filepath:
            filepath,line = filepath.split(':')
        if self.current_path:
            filepath = os.path.join(self.current_path, filepath)
        # Generate the openurl string
        editor = self.config.plugin_get(self.plugin_name, 'editor')
        openurl = self.config.plugin_get(self.plugin_name, 'openurl')
        openurl = openurl.replace('{editor}', editor)
        openurl = openurl.replace('{filepath}', filepath)
        openurl = openurl.replace('{line}', line)
        # Check we are opening the file
        if self.is_called_by_open():
            subprocess.call(shlex.split(openurl))
            return '--version'
        return openurl
