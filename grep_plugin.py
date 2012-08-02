# michele.silva@gmail.com
# GPL v2

""" Terminator plugin to open grep output using a chosen editor. 
Currently supports gvim and gedit.
"""
import re
import terminatorlib.plugin as plugin
import terminatorlib.config as config

# Every plugin you want Terminator to load *must* be listed in 'AVAILABLE'
AVAILABLE = ['GrepPlugin']

class GrepPlugin(plugin.URLHandler):
    """Process URLs returned by the grep command."""

    capabilities = ['url_handler']
    handler_name = 'grepurl'
    nameopen = "Open in editor"
    namecopy = "Copy editor URL"
    match = '[^ \t\n\r\f\v:]+?[:]([0-9]+?[:])?'


    def __init__(self):
       self.plugin_name = self.__class__.__name__
       self.current_path = None
       self.config = config.Config()
       current_config = self.config.plugin_get_config(self.plugin_name)

       # Default editor
       if not current_config:
          self.config.plugin_set(self.plugin_name, 'editor', 'gvim')
          self.config.plugin_set(
             self.plugin_name, 'options', "--remote-silent") 
          self.config.save()


    def set_editor(self, editor):
        """Set the path to the editor used to open the file.
        """
        self.config.plugin_set(self.plugin_name, 'editor', editor)
        config.save()


    def is_called_by_open(self):
        """A hack to check if it is being called by the open_url function. 

        WARNING: inspection should be used in logging and debugging.
        It is being used here because Terminator does not support 
        plugins' custom url handlers."""
        import inspect
        # open_url (3) -> prepare_url (2) -> callback (1)
        return inspect.stack()[3][3] == "open_url"


    def open_file(self, file_url, line_number):
        """Open the file using the current editor.
        """
        import os
        import subprocess

        if self.current_path:
            file_url = os.path.join(self.current_path, file_url)

        args = [
            self.config.plugin_get(self.plugin_name, 'editor'), 
            '+' + line_number,
            file_url, 
        ]

        # insert options
        options = self.config.plugin_get(self.plugin_name, 'options').split()
        args = args[:1] + options + args[1:]

        subprocess.call(args)
        
    
    def callback(self, url):
        """Replace :line_number by +line_number."""
       
        # vte returns the full string, so we must remove the :
        url = url[:-1]
        if ':' in url:
            url, line_number = url.split(':')
        else:
            line_number = '0'

        if self.is_called_by_open():
            self.open_file(url, line_number)
            # Hack to skip calling 'xdg-open' on the url
            return '--version'
        
        return '{} {} +{}'.format(
            self.config.plugin_get(self.plugin_name, 'editor'),
            url,
            line_number,
        )

