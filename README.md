Summary
---------
Debugging javascript can be tedious due to the lack of integration between the code editor and the browsers' debugging tools. JsDebuggr aims to make it a tad easier by allowing Sublime Text to mark breakpoints for the web browser debugging tools.  

The way it works is by adding the `debugger` keyword to the specified line. If the web browser's dev tools window is opened, this keyword acts as a breakpoint, giving the user an opportunity to review variable values, the call stack, etc.

Features
--------
JsDebuggr can add, remove, enable, and disable breakpoints. It can also create conditional breakpoints, that will only trigger if a provided condition is met. It can also scan files for existing `debugger` statements and add breakpoints for those statements. In the future, it will be able to store breakpoint sets for easy swapping of debugging tasks.


Settings
--------
JsDebuggr has only a handful of settings for now. They can be found in the `JsDebuggr.sublime-settings` file.  

* `scan_on_load` indicates if files should be scanned for existing `debugger` statements when a document is loaded.
* `file_type_list` is an array of file extensions that should be scanned. The default extensions are html and js.


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
