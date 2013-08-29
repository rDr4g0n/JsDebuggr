Summary
---------
Debugging javascript can be tedious due to the lack of integration between the code editor and the browsers' debugging tools. JsDebuggr aims to make it a tad easier by allowing the user to easily manage breakpoints from the Sublime Text editor.  

The way JsDebuggr works is by inserting the `debugger` keyword at each breakpoint when the document is saved. Since this happens only when the document is saved, the user never sees the breakpoints. They just work :D

![ScreenShot](https://raw.github.com/rDr4g0n/JsDebuggr/master/screens2.gif)

Of course, the js engine executing the code needs to support the `debugger` keyword and debugging needs to be enabled (in Chrome, for instance, the developer console must be open).


Features
--------
* Add and remove individual breakpoints, or remove all breakpoints at once.
* Enable and disable individual breakpoints or all at once.
* Create conditional breakpoints.
* Breakpoints stay in your document.
* The underlying `debugger` stuff is hidden away where you don't have to look at it (and where it won't annoy your linter, who is already quite mad at me anyway).
* Breakpoints work in injected or eval'd code, which is difficult or not possible with browser dev tools.


Installation
------------
Clone the repo to your Sublime Text `Packages folder`. Something like this should work: `C:\Users\User\AppData\Roaming\Sublime Text 3\Packages\JsDebuggr\`


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
JsDebuggr has only a handful of settings for now. They can be found in the `JsDebuggr.sublime-settings` file.

* `file_type_list` is an array of file extensions that should be enabled for scanning and tracking. The default value is `["html", "htm", "js"]`.
* `autoscan_on_load` is a bool that indicates if a newly loaded doc should be scanned for existing debugger keywords, and those keywords be transformed into breakpoints
* `breakpoint_color`, `conditional_breakpoint_color`, and `disabled_breakpoint_color` determine the color of the gutter icon for breakpoints of various types.
* `verbose` right now JsDebuggr dumps a lot into the console for troubleshooting. Setting this to false will prevent that behavior. Once it is in a better state, this will default to false.

Future Features
-----
* disable context menu options when they are not valid (for instance, "Edit Conditional Breakpoint" should only be visible when a conditional breakpoint is selected).
* save and load of multiple breakpoint sets
* persist disabled breakpoints through document close/open (regular and contional breakpoints persist, but disabled breakpoints do not)
* multiple selection support
