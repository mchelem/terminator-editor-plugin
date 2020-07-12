Terminator Editor Plugin
----------------------
Terminator plugin to open a file uri, including line number, in an editor. 
When the configured regex is matched, you can click the link and open the file in a previously configured editor.
See the demo at https://github.com/mchelem/terminator-editor-plugin/wiki.


### Installing the Plugin ###
* Create the plugins folder if it doesn't exist. On linux: `mkdir -p ~/.config/terminator/plugins`
* Copy the plugin file to the plugins folder.
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
    command = "gvim --remote-silent +"call cursor({line}, {column})" {filepath}"

    command = gedit +{line} {filepath}

    command = sublime {filepath}:{line}

    command = emacsclient -n +{line} {filepath}

    command = code --goto {filepath}:{line}:{column}

    command = atom {filepath}:{line}

You can specify the regex to match filenames to your liking.

You can also configure it to open an editor command within the current terminal window (useful for terminal-based editors)
```
open_in_current_term = True
command = vim +{line} {filepath}
```

If your files are not in the current path but in a specific directory,
you may use the libdir config.

```
libdir = ~/libs
```

#### Regex examples

The inputs to the editor may be specified using the groups parameter. By default the first group matched is the filename and the second is the line number (groups = "file line").

File paths with a specified line number (ex: some/file/path.txt:12) **(default)**:

```match = ([^ \t\n\r\f\v:]+?):([0-9]+)```

File paths followed by line number and, optionally, column:

```
match = "([^ \t\n\r\f\v:]+?):([0-9]+):?([0-9]+)?"
groups = "file line column"
```

Specific file types with or without a line number specified:

```match = ([^ \t\n\r\f\v:]+?\.(html|py|css|js|txt|xml|json))[ \n:](([0-9]+)*)```

File paths with or without line numbers and Python stack traces:

```
match = ([^ \t\n\r\f\v:"]+[\.\/][^ \t\n\r\f\v:"]+)?(". line |:)([0-9]+)*
groups = "file separator line"
```

Warning: Use quotes in your parameters if you want to include a comma.

