# JsDebuggr v.5

import sublime
import sublime_plugin
import uuid
import re

# TODO - put these vars into a config file
BREAK_SCOPE = "keyword"
CONDITIONAL_SCOPE = "string"
DEBUG_STATEMENT = "debugger; "


#collection containing a list of breakpoints and a number
#of functions for retrieving, removing, sorting, and also
#handles drawing the breakpoint circle in the gutter
class BreakpointList():
    def __init__(self, view):
        self.breakpoints = {}
        self.numLines = 0
        self.view = view

    def get(self, lineNum):
        lineNumStr = str(lineNum)
        if lineNumStr in self.breakpoints:
            return self.breakpoints[lineNumStr]
        else:
            return None

    #returns True if a new break is created. returns
    #false if the break existed but is now removed
    def toggle(self, lineNum):
        if lineNum is None:
            return

        lineNumStr = str(lineNum)

        #check if breakpoint is already stored
        if lineNumStr in self.breakpoints:
            self.remove(lineNum)
            return False
        #create a new Breakpoint
        else:
            self.add(lineNum)
            return True

    def add(self, lineNum):
        lineNumStr = str(lineNum)

        #setup breakpoint
        debugger = DEBUG_STATEMENT
        scope = BREAK_SCOPE

        #TODO - conditional break

        print("creating new breakpoint for line %i" % lineNum)
        breakpoint = Breakpoint(**{
            "lineNum": lineNum,
            "enabled": True,
            "scope": scope,
            "debugger": debugger
        })
        #register breakpoint
        self.breakpoints[lineNumStr] = breakpoint

        #TODO - make this line region lookup simpler...
        line = self.view.line(self.view.text_point(lineNum - 1, 0))
        self.view.add_regions(breakpoint.id, [line], breakpoint.scope, "circle", sublime.HIDDEN | sublime.PERSISTENT)

        return breakpoint

    def remove(self, lineNum):
        lineNumStr = str(lineNum)
        print("removing breakpoint for line %s" % lineNumStr)
        self.view.erase_regions(self.breakpoints[lineNumStr].id)
        #remove from breakpoints registry
        del self.breakpoints[lineNumStr]

    def remove_all(self):
        #TODO - creating lineNumList can be done in a more pythonic way
        #   im just not sure what it is. once I figure that out i can
        #   make this just one loop instead of 2
        lineNumList = []
        for id in self.breakpoints:
            lineNumList.append(id)
        for lineNum in lineNumList:
            self.remove(lineNum)

    #adjusts breakpoint line numbers due to insertions/removals
    #TODO - this should prolly be more... generic. or placed elsewhere?
    def shift(self, added, cursorLine):
        newBreakpoints = {}

        #any breakpoint with a lineNum > cursorLine should be updated
        for lineNum in self.breakpoints:
            lineNumInt = int(lineNum)
            newLineNumInt = lineNumInt + added
            newLineNumStr = str(newLineNumInt)

            print([lineNumInt, cursorLine])
            #if lines were removed and this breakpoint is within
            #the removal, it should be removed from the list
            if (
                added < 0 and lineNumInt > cursorLine and
                lineNumInt <= cursorLine - added
            ):
                print("removing breakpoint at line %s - line has been deleted" % lineNum)
                self.view.erase_regions(self.breakpoints[lineNum].id)
            #if this breakpoint is beyond the cursor, it needs to shift
            #TODO - select end of breakpointed line and hit enter. it will incorrectly
            #   shift this line :( need to know if the line was actually moved, or if a
            #   new line was inserted below
            elif (
                added > 0 and lineNumInt >= cursorLine-1 or
                added < 0 and lineNumInt > cursorLine
            ):
                newBreakpoints[newLineNumStr] = self.breakpoints[lineNum]
                newBreakpoints[newLineNumStr].lineNum = newLineNumInt
                print("moving %i to %i" % (lineNumInt, newLineNumInt))
                print("lineNum is %s" % newBreakpoints[newLineNumStr].lineNum)
            #otherwise, leave it where it is
            else:
                newBreakpoints[lineNum] = self.breakpoints[lineNum]

        #update the global breakpoint list with the new one
        #TODO - redraw all breakpoint icons?
        self.breakpoints = newBreakpoints


#model containing information about each breakpoint
class Breakpoint():
    def __init__(self, lineNum=0, lineText="", enabled=True, scope=BREAK_SCOPE, debugger=DEBUG_STATEMENT, conditional=False):
        self.id = str(uuid.uuid4())
        self.lineNum = lineNum
        self.lineText = lineText
        self.enabled = True
        self.scope = scope
        self.debugger = debugger
        self.conditional = conditional


# handle text commands from user
class JsDebuggr(sublime_plugin.TextCommand):

    breakpointLists = {}

    def run(self, edit, **options):
        breakpointList = self.get_breakpointList(self.view)

        if(options and "removeAll" in options):
            breakpointList.remove_all()
        else:
            self.toggle_break()

    def get_line_nums(self):
        lineNums = []
        for s in self.view.sel():
            lineNums.append(self.view.rowcol(s.a)[0] + 1)
        return lineNums

    def get_breakpointList(self, view):
        viewId = str(view.id())
        if not viewId in self.breakpointLists:
            print("creating new BreakpointList")
            self.breakpointLists[viewId] = BreakpointList(view)

        return self.breakpointLists[viewId]

    def toggle_break(self):
        breakpointList = self.get_breakpointList(self.view)

        #assuming we want to toggle breakpoint for now
        #TODO - deal with multiple selection
        lineNum = self.get_line_nums()[0]

        breakpoint = breakpointList.get(lineNum)

        if breakpoint:
            #breakpoint exists, so turn it off.
            breakpointList.remove(lineNum)
        else:
            #else, create a new one
            breakpoint = breakpointList.add(lineNum)


#write the debugger; statements to the document before save
class WriteDebug(sublime_plugin.TextCommand):
    def run(self, edit):
        #iterate breakpoints and write debugger; statments
        breakpointList = JsDebuggr.get_breakpointList(JsDebuggr, self.view)
        for id in breakpointList.breakpoints:
            breakpoint = breakpointList.breakpoints[id]
            point = self.view.text_point(int(breakpoint.lineNum)-1, 0)
            self.view.insert(edit, point, breakpoint.debugger)


#remove debugger; statements from the document after save
class ClearDebug(sublime_plugin.TextCommand):
    def run(self, edit):
        breakpointList = JsDebuggr.get_breakpointList(JsDebuggr, self.view)
        for id in breakpointList.breakpoints:
            breakpoint = breakpointList.breakpoints[id]
            line = self.view.line(self.view.text_point(breakpoint.lineNum-1, 0))
            dedebugged = self.view.substr(line)
            dedebugged = re.sub(r'%s' % re.escape(breakpoint.debugger), '', dedebugged)
            self.view.replace(edit, line, dedebugged)


#listen for events and call necessary functions
class EventListener(sublime_plugin.EventListener):

    numLines = {}
    track = True

    def on_modified(self, view):
        if not self.track:
            return

        viewId = str(view.id())
        breakpointList = JsDebuggr.get_breakpointList(JsDebuggr, view)

        #determine how many lines are in this view
        currNumLines = view.rowcol(view.size())[0] + 1
        # if it doesnt match numLines, evaluate where the lines were inserted/removed
        if currNumLines != self.numLines[viewId]:
            added = currNumLines - self.numLines[viewId]
            print("omg %i lines added!" % added)
            #use the cursor position to guess where the lines were inserted/removed
            #NOTE - this only supports single cursor operations
            cursorLine = view.rowcol(view.sel()[0].a)[0] + 1
            #TODO - shift method might need a refactor/rename
            breakpointList.shift(added, cursorLine)

            #update new number of lines
            self.numLines[viewId] = currNumLines

    def on_pre_save(self, view):
        if not self.track:
            return

        #insert debugger; statments
        view.run_command("write_debug")
        pass

    def on_post_save(self, view):
        if not self.track:
            return

        #TODO - remove debugger; statments
        view.run_command("clear_debug")
        pass

    def on_load(self, view):
        settings = sublime.load_settings("JsDebuggr.sublime-settings")

        file_type_list = settings.get("file_type_list")
        print(file_type_list)
        extension = view.file_name().split(".")[-1]
        if not extension in file_type_list:
            print("Not tracking document because it is not of the correct type.")
            self.track = False
            #TODO - remove event listeners?
            #TODO - remove right click menu?
            return

        viewId = str(view.id())

        #if the number of lines has not been recorded, record it
        if not viewId in self.numLines:
            self.numLines[viewId] = view.rowcol(view.size())[0] + 1
            print("setting numlines to %i" % self.numLines[viewId])
        #force create breakpoint list
        JsDebuggr.get_breakpointList(JsDebuggr, view)
