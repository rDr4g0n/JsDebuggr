JsDebuggr
Debugging javascript can be tedious due to the lack of integration between the code editor and the browsers' debugging tools. JsDebuggr aims to make it a tad easier by allowing Sublime Text to mark breakpoints for the web browser debugging tools.

The way it works is by adding the "debugger" keyword to the specified line. If the web browser's dev tools window is opened, this keyword acts as a breakpoint, giving the user an opportunity to review variable values, the call stack, etc.

JsDebuggr takes care of adding and removing breakpoints, creating conditional breakpoints, and disabling breakpoints.
