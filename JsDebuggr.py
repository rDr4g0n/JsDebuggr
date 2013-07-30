# JsDebuggr v.9

import sublime
import sublime_plugin
import uuid
import re

# TODO - can context menu be edited at runtime? (remove JsDebuggr for non-js files, show context sensitive options, etc)
# TODO - future feature - load, save, delete breakpoint sets

settings = sublime.load_settings("JsDebuggr.sublime-settings")


class JsDebuggr(sublime_plugin.TextCommand):

    breakpoints = {}

    def run(self, edit, **options):
        viewId = str(self.view.id())
        #lineNum = self.get_line_nums()[0]

        #if this view has not been registered yet, register it
        if not viewId in self.breakpoints:
            print("adding this view to breakpoints")
            self.breakpoints[viewId] = {}

        if(options and "clearAll" in options):
            print("clearing all breaks")
            self.clear_all(edit)
        elif(options and "toggleEnable" in options):
            print("enabling breakpoint")
            self.toggle_enable_breakpoint(edit)
        elif(options and "enableAll" in options):
            print("enabling all breakpoint")
            self.enable_all(edit)
        elif(options and "disableAll" in options):
            print("disabling all breakpoint")
            self.disable_all(edit)
        elif(options and "addBreakpointProxy" in options):
            self.add_breakpoint_proxy(edit, options["addBreakpointProxy"])
        elif(options and "removeBreakpointProxy" in options):
            self.remove_breakpoint_proxy(edit, options["removeBreakpointProxy"])
        else:
            self.toggle_breakpoint(edit)

    def toggle_breakpoint(self, edit):
        viewId = str(self.view.id())

        print("----------------")

        lineNum = self.get_line_nums()[0]

        #find the line that this selection is on
        lineNumStr = str(lineNum)

        #check if breakpoint is already stored
        if lineNumStr in self.breakpoints[viewId]:
            self.remove_breakpoint(edit, viewId, lineNum)
        #create a new Breakpoint
        else:
            self.add_breakpoint(edit, viewId, lineNum)

    def toggle_enable_breakpoint(self, edit):
        viewId = str(self.view.id())

        print("----------------")

        lineNum = self.get_line_nums()[0]

        #find the line that this selection is on
        lineNumStr = str(lineNum)

        #check if breakpoint is already stored
        if lineNumStr in self.breakpoints[viewId]:
            #check if its enabled or disabled
            breakpoint = self.breakpoints[viewId][lineNumStr]
            if breakpoint.enabled:
                breakpoint.disable(self.view, edit)
            else:
                breakpoint.enable(self.view, edit)

    def add_breakpoint(self, edit, viewId, lineNum):
        #setup breakpoint
        debugger = "debugger;"
        scope = settings.get("breakpoint_color_enabled")

        print("creating new breakpoint for line %i" % lineNum)
        breakpoint = Breakpoint(**{
            "lineNum": lineNum,
            "enabled": True,
            "scope": scope,
            "debugger": debugger
        })
        #register breakpoint
        self.breakpoints[viewId][str(lineNum)] = breakpoint
        #add breakpoint to the view
        breakpoint.add(self.view, edit)

    def remove_breakpoint(self, edit, viewId, lineNum):
        lineNumStr = str(lineNum)
        print("breakpoint for line %s already exists" % lineNumStr)
        self.breakpoints[viewId][lineNumStr].remove(self.view, edit)
        #remove from breakpoints registry
        del self.breakpoints[viewId][lineNumStr]

    def add_conditional(self, edit, condition):
        viewId = str(self.view.id())
        lineNum = self.view.rowcol(self.view.line(self.get_line_nums()[0]).a)[0] + 1

        debugger = " if(%s){ debugger; }" % condition[0]
        scope = settings.get("breakpoint_color_conditional")
        print("breakpoint.debugger = %s" % debugger)

        print("creating new breakpoint for line %i" % lineNum)
        breakpoint = Breakpoint(**{
            "lineNum": lineNum,
            "enabled": True,
            "scope": scope,
            "debugger": debugger,
            "conditional": True
        })
        #register breakpoint
        self.breakpoints[viewId][str(lineNum)] = breakpoint
        #add breakpoint to the view
        breakpoint.add(self.view, edit)

    def clear_all(self, edit):
        viewId = str(self.view.id())

        for lineNum in self.breakpoints[viewId]:
            self.breakpoints[viewId][lineNum].remove(self.view, edit)

    def disable_all(self, edit):
        viewId = str(self.view.id())

        for lineNum in self.breakpoints[viewId]:
            self.breakpoints[viewId][lineNum].disable(self.view, edit)

    def enable_all(self, edit):
        viewId = str(self.view.id())

        for lineNum in self.breakpoints[viewId]:
            self.breakpoints[viewId][lineNum].enable(self.view, edit)

    def get_line_nums(self):
        lineNums = []
        for s in self.view.sel():
            lineNums.append(self.view.rowcol(s.a)[0] + 1)
        return lineNums

    #silly hack to get access to an edit object :/
    def add_breakpoint_proxy(self, edit, lineNum):
        viewId = str(self.view.id())
        breakpoint = self.breakpoints[viewId][lineNum]
        breakpoint.add(self.view, edit)

    #silly hack to get access to an edit object :/
    def remove_breakpoint_proxy(self, edit, lineNum):
        viewId = str(self.view.id())
        breakpoint = self.breakpoints[viewId][lineNum]
        breakpoint.remove(self.view, edit)


class ConditionalBreakpoint(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_input_panel("Enter Condition:", "", self.on_done, None, None)

    def on_done(self, text):
        view = self.window.active_view()
        viewId = str(view.id())
        lineNum = view.rowcol(view.line(view.sel()[0]).a)[0] + 1

        #if a breakpoint exists here, clear it
        if str(lineNum) in JsDebuggr.breakpoints[viewId]:
            #HACK - since we dont have an edit object, we need to proxy the
            #       remove method through a TextCommand on js_debuggr
            view.run_command("js_debuggr", {"removeBreakpointProxy": str(lineNum)})

        #setup conditional breakpoint
        debugger = "if(%s){ debugger; }" % text
        scope = settings.get("breakpoint_color_conditional")
        print("breakpoint.debugger = %s" % debugger)

        print("creating new conditional breakpoint for line %i" % lineNum)
        breakpoint = Breakpoint(**{
            "lineNum": lineNum,
            "enabled": True,
            "scope": scope,
            "debugger": debugger,
            "conditional": True
        })
        #register breakpoint
        JsDebuggr.breakpoints[viewId][str(lineNum)] = breakpoint

        #HACK - since we dont have an edit object, we need to proxy the
        #       add method through a TextCommand on js_debuggr
        #add breakpoint to the view
        #breakpoint.add(view, edit)
        view.run_command("js_debuggr", {"addBreakpointProxy": str(lineNum)})


class Breakpoint():

    def __init__(self, lineNum=0, enabled=True, scope=settings.get("breakpoint_color_enabled"), debugger="debugger;", conditional=False):
        self.id = str(uuid.uuid4())
        self.lineNum = lineNum
        self.enabled = True
        self.scope = scope
        self.debugger = debugger
        self.conditional = conditional

    def add(self, view, edit, dontProcessDebug=False, dontInsertDebug=False):
        if not self.lineNum:
            print("cannot add breakpoint. missing lineNum")
            return

        print("adding breakpoint for line %i" % self.lineNum)
        line = view.line(view.text_point(self.lineNum-1, 0))

        #display breakpoint marker
        view.add_regions(self.id, [line], self.scope, "circle", sublime.HIDDEN | sublime.PERSISTENT)

        #if text should be inserted/updated for this breakpoint
        if not dontInsertDebug:
            insertion = self.process_insertion(view, line)
            # if this breakpoint has already been processed before, dont update self.debugger
            if not dontProcessDebug:
                self.debugger = insertion[1]
            view.insert(edit, insertion[0], self.debugger)

    def remove(self, view, edit):
        line = view.line(view.text_point(self.lineNum-1, 0))

        print("removing breakpoint at line %i" % self.lineNum)
        #delete the debugger statement
        dedebugged = view.substr(line)
        print("this debug statement is %s" % self.debugger)
        print("this line is '%s'" % dedebugged)
        dedebugged = re.sub(r'%s' % re.escape(self.debugger), '', dedebugged)
        view.replace(edit, line, dedebugged)
        #clear the region
        view.erase_regions(self.id)
        #TODO - prevent the cursor from moving when removing breakpoint

    def disable(self, view, edit):
        line = view.line(view.text_point(self.lineNum-1, 0))

        self.scope = settings.get("breakpoint_color_disabled")
        self.enabled = False

        print("disabling breakpoint at line %i" % self.lineNum)
        #delete the debugger statement
        #TODO - factor this regex thing into a function
        dedebugged = view.substr(line)
        print("this debug statement is %s" % self.debugger)
        print("this line is '%s'" % dedebugged)
        dedebugged = re.sub(r'%s' % re.escape(self.debugger), '', dedebugged)
        view.replace(edit, line, dedebugged)
        #TODO - prevent the cursor from moving when removing breakpoint
        #display breakpoint marker
        view.add_regions(self.id, [line], self.scope, "circle", sublime.HIDDEN | sublime.PERSISTENT)

    def enable(self, view, edit):
        self.scope = settings.get("breakpoint_color_enabled")
        if self.conditional:
            self.scope = settings.get("breakpoint_color_conditional")
        self.enabled = True

        self.add(view, edit, True)

    def process_insertion(self, view, line):
        lineContent = view.substr(line)
        #where to insert the debugger statement
        insertionPoint = line.b
        debugger = self.debugger
        #statement portion of the line. excludes comments
        statement = lineContent

        #TODO - the program flow here is horrible. make it graceful
        #deal with comments, semicolons, and bears
        #if this line contains a comment, place the breakpoint before the comment
        commentMatch = re.search(r'\/\/', lineContent)
        if commentMatch:
            #if this comment is the only thing on the line
            print("start: %i, line.a: %i" % (commentMatch.start(0), line.a))
            if commentMatch.start(0) == 0:
                insertionPoint = line.a + commentMatch.start(0)
                debugger = "%s " % debugger
                #no need to do semicolon insertion
                statement = ""
                print("this line is a comment. adding debugger ahead of comment")
            #otherwise, this is a statement with a comment after it
            else:
                insertionPoint = line.a + commentMatch.start(0) - 1
                debugger = " %s" % debugger
                #we want semicolon insertion to search BEFORE the comment
                statement = lineContent[:commentMatch.start(0)]
                print("this line contains a comment. adding debugger ahead of comment")
        else:
            # grab the last non-whitespace character in this line
            for match in re.finditer(r'\S', statement):
                pass
            #if it isnt a semicolon, add one
            if match.group(0) != ";":
                debugger = "; %s" % debugger
                print("last char is %s, adding semicolon" % match.group(0))
            else:
                debugger = " %s" % debugger

        return [insertionPoint, debugger]


class DocUpdate(sublime_plugin.EventListener):

    numLines = {}
    process = False

    def on_load(self, view):
        viewId = str(view.id())

        print("----------")

        #determine if this document should be processed by this plugin
        file_type_list = settings.get("file_type_list")
        scan_on_load = settings.get("scan_on_load")
        extension = view.file_name().split(".")[-1]
        print("file extension is %s" % extension)
        if not scan_on_load:
            print("not scanning doc, per settings")
            return
        elif not extension in file_type_list:
            print("not a js or html doc, so not scanning")
            return
        else:
            self.process = True

        #if this view has not been registered yet, register it
        if not viewId in JsDebuggr.breakpoints:
            print("adding this view to breakpoints")
            JsDebuggr.breakpoints[viewId] = {}

        self.numLines[viewId] = view.rowcol(view.size())[0] + 1

        print("checking for existing debugger statments")

        #scan the document for debugger;
        #TODO - deal with autoscanning conditional statements
        #TODO - overall this auto scanning thing is kinda squirrely
        results = view.find_all("debugger;")
        if results:
            for r in results:
                lineNum = view.rowcol(r.a)[0] + 1

                #TODO - account for conditional breakpoints
                print("creating new breakpoint for line %i" % lineNum)
                breakpoint = Breakpoint(**{
                    "lineNum": lineNum,
                    "enabled": True,
                    "scope": settings.get("breakpoint_color_enabled"),
                    "debugger": "debugger;"
                })
                #register breakpoint
                JsDebuggr.breakpoints[viewId][str(lineNum)] = breakpoint
                #add breakpoint line marker to view
                view.add_regions(breakpoint.id, [r], breakpoint.scope, "circle", sublime.HIDDEN | sublime.PERSISTENT)

    def on_modified(self, view):
        if not self.process:
            print("not a js or html doc, so not processing")
            return

        viewId = str(view.id())

        if not viewId in self.numLines:
            self.numLines[viewId] = view.rowcol(view.size())[0] + 1

        #determine how many lines are in this view
        currNumLines = view.rowcol(view.size())[0] + 1
        # if it doesnt match numLines, evaluate where the lines were inserted/removed
        if currNumLines != self.numLines[viewId]:
            added = currNumLines - self.numLines[viewId]
            print("omg %i lines added!" % added)
            #use the cursor position to guess where the lines were inserted/removed
            #NOTE - this only supports single cursor operations
            cursorLine = view.rowcol(view.sel()[0].a)[0] + 1

            #if there are any breakpoints for this view
            if viewId in JsDebuggr.breakpoints:
                newBreakpoints = {}

                #any breakpoint with a lineNum > cursorLine should be updated
                for lineNum in JsDebuggr.breakpoints[viewId]:
                    lineNumInt = int(lineNum)
                    newLineNumInt = lineNumInt + added
                    newLineNumStr = str(newLineNumInt)
                    if lineNumInt > cursorLine-2:
                        newBreakpoints[newLineNumStr] = JsDebuggr.breakpoints[viewId][lineNum]
                        newBreakpoints[newLineNumStr].lineNum = newLineNumInt
                        print("moving %i to %i" % (lineNumInt, newLineNumInt))
                        print("lineNum is %s" % newBreakpoints[newLineNumStr].lineNum)
                    else:
                        newBreakpoints[lineNum] = JsDebuggr.breakpoints[viewId][lineNum]

                #update the global breakpoint list with the new one
                JsDebuggr.breakpoints[viewId] = newBreakpoints

            #update new number of lines
            self.numLines[viewId] = currNumLines
