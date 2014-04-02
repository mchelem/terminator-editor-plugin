terminator-grep-plugin
----------------------
Terminator plugin to open grep output using a chosen editor
See the demo at https://github.com/mchelem/terminator-grep-plugin/wiki.


### Installing the plugin ###
* Copy the plugin file to `~/.config/terminator/plugins`.
* In Terminator go to Preferences >> Plugins and enable GrepPlugin.
* Restart Terminator.


### Using the plugin ###
- Use the grep command (e.g. <code>grep -rn import *.py</code>)
- Use &lt;ctrl&gt;+click to open the file.
- Right click to copy the link.


### Configuration ###
The configuration file is located at `~/.config/terminator/config`. Update
the command under the `[[GrepPlugin]]` section to suit your needs. A few
examples are below:

    command = gvim --remote-silent {filepath} +{line}
    command = vim -g --remote-tab {filepath} +{line}
    command = sublime {filepath}:{line}
