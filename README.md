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

You can specify the regex to match filenames to your liking.

#### Regex examples

File paths with a specified line number (ex: some/file/path.txt:12) **(default)**:

```match = ([^ \t\n\r\f\v:]+?):([0-9]+)```

Specific file types with or without a line number specified:

```match = ([^ \t\n\r\f\v:]+?\.(html|py|css|js|txt|xml|json))[ \n:](([0-9]+)*)```

File paths with or without line numbers and Python stack traces:

```match = ([^ \t\n\r\f\v:"]+[\.\/][^ \t\n\r\f\v:"]+)?(". line |:)([0-9]+)* ```

Warning: Inside terminator the regexes are split by comma, so be careful not to include the ',' character in your regex.

