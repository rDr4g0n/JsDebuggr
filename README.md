Summary
---------
Debugging javascript can be tedious due to the lack of integration between the code editor and the browsers' debugging tools. JsDebuggr aims to make it a tad easier by allowing the user to easily manage breakpoints from the Sublime Text editor.  

The way JsDebuggr works is by inserting the `debugger` keyword at each breakpoint when the document is saved. Since this happens only when the document is saved, the user never sees the breakpoints. They just work :D

![ScreenShot](screens3.gif)

Of course, the js engine executing the code needs to support the `debugger` keyword and debugging needs to be enabled (in Chrome, for instance, the developer console must be open).


Features
--------
Hey this thing is purty neat. Check it out:
* Add and remove individual breakpoints, or remove all breakpoints at once.
* Enable and disable individual breakpoints or all at once.
* Create conditional breakpoints.
* Breakpoints stay in your document, so you can save and close, and later open it and they will still be there.
* The underlying `debugger` stuff is hidden away where you don't have to look at it (and where it won't annoy your linter, who is already quite mad at me anyway).
* Breakpoints work in injected, concatted, processed, and eval'd code. It is often difficult or not possible to add breakpoints in browser dev tools.
* Breakpoints stick to the line you want them to stick to and move when your code does. In browser dev tools, the breakpoints are absolutely assigned to a line number, so if you add or remove lines in your source, next time your refresh the page, the breakpoints from the browser dev tool will annoyingly be off by *n* number of lines.

As in any wonderful relationship, there are down sides :(
* You can't add or remove breakpoints during runtime. This can be frustrating when you want to turn off a breakpoint, but you don't want to reload the page (maybe you have a complex state you don't want to lose).
* You have to save the document everytime you add, remove, or update a breakpoint.


What This Isn't
---------------
This plugin is not a developer console replacement. You will still need to open firebug or chrome dev tools or enable debugging in node.js, and use those tools to examine the stack, vars, etc. This plugin doesn't connect to those dev tools in any way.


Installation
------------
From Sublime Text 3, assuming Package Control is installed, press `ctrl+shift+p` (Win, Linux) or cmd+shift+p (OS X) and start typing "Install Package". Select "Package Control: Install Package" from the list, then start typing "jsdebuggr", and select the package for install.  


Usage
-----
Simply add a breakpoint and then *save the document*. This will add the `debugger` keywords behind the scenes, so when your document is loaded in a js engine that supports it, it will break at that point. Note that you *must save the document* manually to make the breakpoints active.

The default key bindings are as follows:

* `ctrl + f10` - add or remove breakpoint
* `ctrl + shift + f10` - disable or enable breakpoint
* `alt + f10` - add a conditional breakpoint

Additionally, the right click menu allows for:

* add/remove breakpoint
* edit conditional breakpoint
* enable/disable breakpoint
* enable/disable all
* remove all

TODO
---------
* more efficient is enabled checks for commands
	* dont load anything if the syntax isnt supported
	* dont check specific line scope for every option in the right click menu
* click gutter to add breakpoint?
* right click gutter to edit breakpoint?
* store debugger text region, then delete after save (instead of regex)
* can probably get rid of debuggerRe field on language def
* more languages (coffeescript, python?, others?)
* show conditional as phantom?
* add some sorta global breakpoint disable in js-land so users can disable breakpoints in their debugger
* multiple selection support
* config option to completely disable
* config option to toggle debug logging
* logpoints?