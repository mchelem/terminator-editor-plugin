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
DEFAULT_COMMAND = 'gvim --remote-silent +{line} {filepath}'
DEFAULT_REGEX = '[^ \\t\\n\\r\\f\\v:]+?:[0-9]+'
REPLACE = {'\\t':'\t', '\\n':'\n', '\\r':'\r', '\\f':'\f', '\\v':'\v'}


class GrepPlugin(plugin.URLHandler):
    """ Process URLs returned by the grep command. """
    capabilities = ['url_handler']
    handler_name = 'grepurl'
    nameopen = 'Open File'
    namecopy = 'Copy Open Command'
    match = None

    def __init__(self):
        self.plugin_name = self.__class__.__name__
        self.current_path = None
        self.config = config.Config()
        self.check_config()
        self.match = self.config.plugin_get(self.plugin_name, 'match')
        for key,val in REPLACE.iteritems():
            self.match = self.match.replace(key, val)

    def check_config(self):
        updated = False
        config = self.config.plugin_get_config(self.plugin_name)
        if not config:
            config = {}
            updated = True
        if 'command' not in config:
            config['command'] = DEFAULT_COMMAND
            updated = True
        if 'match' not in config:
            config['match'] = DEFAULT_REGEX
            updated = True
        if updated:
            self.config.plugin_set_config(self.plugin_name, config)
            self.config.save()

    def get_cwd(self):
        """ Return current working directory. """
        # HACK: Because the current working directory is not available to plugins,
        # we need to use the inspect module to climb up the stack to the Terminal
        # object and call get_cwd() from there.
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

    def callback(self, strmatch):
        strmatch = strmatch.strip(':').strip()
        filepath = os.path.join(self.get_cwd(), strmatch.split(':')[0])
        lineno = strmatch.split(':')[1] if ':' in strmatch else '1'
        with open('/tmp/logs.log', 'a') as handle:
            handle.write('---\n')
            handle.write('strmatch: %s\n' % strmatch)
            handle.write('filepath: %s\n' % filepath)
            handle.write('lineno: %s\n' % lineno)
            # Generate the openurl string
            command = self.config.plugin_get(self.plugin_name, 'command')
            handle.write('command: %s\n' % command)
            command = command.replace('{filepath}', filepath)
            handle.write('command: %s\n' % command)
            command = command.replace('{line}', lineno)
            handle.write('command: %s\n' % command)
        # Check we are opening the file
        if self.open_url():
            subprocess.call(shlex.split(command))
            return '--version'
        return command
