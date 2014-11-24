Terminator Editor Plugin
----------------------
Terminator plugin to open a file uri, including line number, in an editor. 
When the configured regex is matched, you can click the link and open the file in a previously configured editor.
See the demo at https://github.com/mchelem/terminator-editor-plugin/wiki.


### Installing the Plugin ###
* Copy the plugin file to `~/.config/terminator/plugins`.
* In Terminator go to Preferences >> Plugins and enable EditorPlugin.
* Restart Terminator.


### Using the Plugin ###
- Use the grep command (e.g. <code>grep -rn import *.py</code>)
- Use &lt;ctrl&gt;+click to open the file.
- Right click to copy the link.


### Configuration ###
The configuration file is located at `~/.config/terminator/config`. Update
the command under the `[[EditorPlugin]]` section to suit your needs. A few
examples are below:

    command = gvim --remote-silent +{line} {filepath} 
    command = vim -g --remote-tab +{line} {filepath} 
    command = gedit +{line} {filepath} 
    command = sublime {filepath}:{line}
    command = emacsclient -n +{line} {filepath}

You can specify the regex to match filenames to your liking. By default the
first example below is used. It will match all file paths with a specified
line number (ex: some/file/path.txt:12). The second example below can match
specific file types with or without a line number specified:

    match = [^ \t\n\r\f\v:]+?:[0-9]+
    match = [^ \t\n\r\f\v:]+?\.(html|py|css|js|txt|xml|json)[ \n:]([0-9]+)*

