Summary
---------
NOTE: In the process of a refactor!

TODO
----------
* python support (artibrary language support)
	* debug statement
	* enable condition
	* disable condition
	* scope to apply to
	* filetype to apply to
* only apply to correct filetype (or context)
* keyboard shortcuts
* Update readme
* package control!

* store regions of breakpoint text when writing and delete region after save?
* show conditional as phantom?
* click gutter to add breakpoint?
* right click gutter to edit breakpoint?
* persist breakpoints via pickle or something?
* settings file
* clear breakpoint regions when jsdebugger reloads
* add some sorta global breakpoint disable in js-land so users can disable breakpoints in their debugger
* multiple selections
* dont load module for view if syntax aint python, js, or html

bugs
------------
* undo can remove a breakpoint region, causing things to splode

Debugging javascript can be tedious due to the lack of integration between the code editor and the browsers' debugging tools. JsDebuggr aims to make it a tad easier by allowing the user to easily manage breakpoints from the Sublime Text editor.  

The way JsDebuggr works is by inserting the `debugger` keyword at each breakpoint when the document is saved. Since this happens only when the document is saved, the user never sees the breakpoints. They just work :D

![ScreenShot](https://raw.github.com/rDr4g0n/JsDebuggr/master/screens2.gif)

Of course, the js engine executing the code needs to support the `debugger` keyword and debugging needs to be enabled (in Chrome, for instance, the developer console must be open).


Features
--------
Hey this thing is purty neat. Check it out:
* Add and remove individual breakpoints, or remove all breakpoints at once.
* Enable and disable individual breakpoints or all at once.
* Create conditional breakpoints.
* Breakpoints stay in your document, so you can save and close, and later open it and they will still be there.
* The underlying `debugger` stuff is hidden away where you don't have to look at it (and where it won't annoy your linter, who is already quite mad at me anyway).
* Breakpoints work in injected or eval'd code. It is often difficult or not possible to add breakpoints in browser dev tools.
* Breakpoints stick to the line you want them to stick to and move when your code does. In browser dev tools, the breakpoints are absolutely assigned to a line number, so if you add or remove lines in your source, next time your refresh the page, the breakpoints from the browser dev tool will annoyingly be off by *n* number of lines.

As in any wonderful relationship, there are down sides :(
* You can't add or remove breakpoints during runtime. This can be frustrating when you want to turn off a breakpoint, but you don't want to reload the page (maybe you have a complex state you don't want to lose).
* You have to save the document everytime you add, remove, or update a breakpoint since (I don't think) Sublime Text's plugin API won't allow a plugin to save the document for you.


What This Isn't
---------------
This plugin is not a developer console replacement. You will still need to open firebug or chrome dev tools or enable debugging in node.js, and use those tools to examine the stack, vars, etc. This plugin doesn't connect to those dev tools in any way. For that, you want a more advanced solution like [Sublime Web Inspector](http://sokolovstas.github.io/SublimeWebInspector/).


Installation
------------
Clone the repo to your Sublime Text `Packages folder`. Something like this should work: `C:\Users\User\AppData\Roaming\Sublime Text 3\Packages\JsDebuggr\`

I will add JsDebuggr to Package Control once I am more confident that it works without any show stopping or code eating bugs.

Usage
-----
Simply add a breakpoint and then *save the document*. This will add the `debugger` keywords behind the scenes, so when your document is loaded in a js engine that supports it, it will break at that point. Note that you *must save the document* manually to make the breakpoints active.

The default key bindings are as follows:

* `ctrl + f10` - add or remove breakpoint
* `ctrl + shift + f10` - disable or enable breakpoint
* `alt + f10` - add a conditional breakpoint

Additionally, the right click menu allows for:

* add/remove breakpoint
* add conditional breakpoint
* edit conditional breakpoint
* remove all
* enable/disable breakpoint
* enable all
* disable all


Settings
--------
JsDebuggr has only a handful of settings, and they're not very useful. They can be found in the `JsDebuggr.sublime-settings` file.

* `file_type_list` is an array of file extensions that should be enabled for scanning and tracking. The default value is `["html", "htm", "js"]`.
* `autoscan_on_load` is a bool that indicates if a newly loaded doc should be scanned for existing debugger keywords, and those keywords be transformed into breakpoints
* `breakpoint_color`, `conditional_breakpoint_color`, and `disabled_breakpoint_color` determine the color of the gutter icon for breakpoints of various types.
* `verbose` right now JsDebuggr dumps a lot into the console for troubleshooting. Setting this to false will prevent that behavior. Once it is in a better state, this will default to false.