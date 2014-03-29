terminator-grep-plugin
======================

Terminator plugin to open grep output using a chosen editor

See the demo at https://github.com/mchelem/terminator-grep-plugin/wiki.

### Installing the plugin
- Find out what is your terminatorlib directory (in ubuntu it is <code>/usr/share/terminator/terminatorlib</code>. For other distros you can try <code>python -c "import terminatorlib; print terminatorlib.\_\_file\_\_"</code>)
- Copy the plugin file to your Terminator plugins directory &lt;terminatorlib dir&gt;/plugins/
- Add one line to the file &lt;terminatorlib dir&gt;/terminal.py
  * Look for <code>urlplugin.callback(url)</code> and add the following line immediately above: 
     * <code>urlplugin.current_path = self.get_cwd()</code>
- Open Terminator
- Go to preferences and enable the GrepPlugin
- Restart Terminator

### Using the plugin
- Use the grep command (e.g. <code>grep -rn import *.py</code>)
- Use &lt;ctrl&gt;+click to open the file.
- Right click to copy the link (link = gvim myfile.my +13). 

### Editing the configuration file
By default, the plugin uses gvim. You can choose another editor, as long as it supports the +line_number syntax, 
by editing Terminator's configuration file. Normally, the configs are stored at <code>/home/&lt;myuser&gt;/.config/terminator/config</code>

* Open the config file, find GrepPugin. You can configure the editor and the editor options.
  * Editor: An editor that accepts the +line_number syntax
  * Options: When using vim --remote, it must be the last option

#### Examples

GVim (default)

    [[GrepPlugin]]  
    editor = gvim
    openurl = {editor} --remote-silent {filepath} +{line}

Vim with tabs (vim only works with the -g option)

    [[GrepPlugin]]  
    editor = vim    
    options = {editor} -g --remote-tab {filepath} +{line}

Gedit

    [[GrepPlugin]]  
    editor = gedit    
    options = 

Sublime

    [[GrepPlugin]]  
    editor = sublime
    options = {editor} {filepath}:{line}