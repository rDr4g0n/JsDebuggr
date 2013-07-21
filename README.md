Summary
---------
Debugging javascript can be tedious due to the lack of integration between the code editor and the browsers' debugging tools. JsDebuggr aims to make it a tad easier by allowing Sublime Text to mark breakpoints for the web browser debugging tools.  

The way it works is by adding the `debugger` keyword to the specified line. If the web browser's dev tools window is opened, this keyword acts as a breakpoint, giving the user an opportunity to review variable values, the call stack, etc.

![ScreenShot](https://raw.github.com/rDr4g0n/JsDebuggr/master/screen1.png)

The benefit of a plugin to do this over entering debugger statements manually is a minor, but noteworthy one: cleaning up or disabling all the debug statements after a long and messy debug session is quick and easy.


Features
--------
JsDebuggr can add, remove, enable, and disable breakpoints. It can also create conditional breakpoints, that will only trigger if a provided condition is met.

JsDebuggr can also scan files for existing `debugger` statements and add breakpoints for those statements. In the future, it will be able to store breakpoint sets for easy swapping of debugging tasks.


Installation
------------
Clone the repo to your Sublime Text `Packages folder`. Something like this should work: `C:\Users\User\AppData\Roaming\Sublime Text 2\Packages\JsDebuggr\`


Settings
--------
JsDebuggr has only a handful of settings for now. They can be found in the `JsDebuggr.sublime-settings` file.  

* `scan_on_load` indicates if files should be scanned for existing `debugger` statements when a document is loaded.
* `file_type_list` is an array of file extensions that should be enabled for scanning and tracking. The default value is `["html", "htm", "js"]`.


Key Bindings
------------
The default key bindings are as follows:

* `ctrl + f10` - add or remove breakpoint
* `alt + f10` - add conditional breakpoint
* `shift + f10` - enable / disable breakpoint

Additionally, the right click menu allows for:

* enable all
* disable all
* clear all


More Details
-------
This is my first ever: python project, sublime plugin, open-source project, github project, etc, so I suspect it needs lots of work... I developed it in ST3, but everything appears to work in ST2. I suspect the code organization can be improved. There are a few hacky bits in there. Also, I know I probably did some things the hard way in places. And hey, maybe I am the only person who will ever use this kind of plugin lol  

There are a few bugs I know about already, and they are mentioned in the .py file mostly for my own reference as I improve stuff.
