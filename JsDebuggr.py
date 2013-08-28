# JsDebuggr 0.5.8

import sublime
import sublime_plugin
import uuid
import re

settings = sublime.load_settings("JsDebuggr.sublime-settings")
BREAK_SCOPE = settings.get("breakpoint_color")
BREAK_DISABLED_SCOPE = settings.get("disabled_breakpoint_color")
CONDITIONAL_SCOPE = settings.get("conditional_breakpoint_color")
FILE_TYPE_LIST = settings.get("file_type_list")
AUTOSCAN_ON_LOAD = settings.get("autoscan_on_load")
VERBOSE = settings.get("verbose")

DEBUG_STATEMENT = "/*JsDbg*/debugger;"
CONDITIONAL_BEGIN_MARKER = "/*JsDbg-Begin*/"
CONDITIONAL_END_MARKER = "/*JsDbg-End*/"

#dict which stores a bool indicating if a view shoul
#be tracked by JsDebuggr. the view id is the dict key
track_view = {}


#TODO - is it ok to leave this guy global like this? seems bad...
def should_track_view(view, force=False):
    viewId = str(view.id())
    #determine if this viewId should be tracked by plugin
    #if this determination hasn't been made before, figure it out
    if not viewId in track_view or force:
        #TODO - use settings instead of hardcoded constants
        #settings = sublime.load_settings("JsDebuggr.sublime-settings")

        file_type_list = FILE_TYPE_LIST
        file_name = view.file_name()
        if not file_name:
            #if this is an unnamed document, don't track
            file_name = ""
        extension = file_name.split(".")[-1]
        if not extension in file_type_list:
            printl("JsDebuggr: Not tracking document because it is not of the correct type.")
            track_view[viewId] = False
            #TODO - remove event listeners?
            #TODO - disable context menu?
        else:
            track_view[viewId] = True

    #printl("JsDebuggr: should_track_view() returning %s" % track_view[viewId])
    return track_view[viewId]


def printl(str):
    if VERBOSE:
        print(str)


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

    def add(self, lineNum, condition=None):
        lineNumStr = str(lineNum)

        #setup breakpoint
        debugger = DEBUG_STATEMENT

        #if there is already a breakpoint for this line, remove it
        if lineNumStr in self.breakpoints:
            self.remove(lineNum)

        printl("JsDebuggr: creating new breakpoint for line %i" % lineNum)
        breakpoint = Breakpoint(**{
            "lineNum": lineNum,
            "enabled": True,
            "debugger": debugger,
            "condition": condition
        })
        #register breakpoint
        self.breakpoints[lineNumStr] = breakpoint

        self.draw_gutter_icon(breakpoint)

        return breakpoint

    def remove(self, lineNum):
        lineNumStr = str(lineNum)
        printl("JsDebuggr: removing breakpoint for line %s" % lineNumStr)
        self.clear_gutter_icon(self.breakpoints[lineNumStr].id)
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

    def enable(self, lineNum):
        lineNumStr = str(lineNum)
        breakpoint = self.breakpoints[lineNumStr]
        breakpoint.enabled = True
        if breakpoint.condition:
            breakpoint.scope = CONDITIONAL_SCOPE
        else:
            breakpoint.scope = BREAK_SCOPE
        self.draw_gutter_icon(breakpoint)

    def disable(self, lineNum):
        lineNumStr = str(lineNum)
        breakpoint = self.breakpoints[lineNumStr]
        breakpoint.enabled = False
        breakpoint.scope = BREAK_DISABLED_SCOPE
        self.draw_gutter_icon(breakpoint)

    def disable_all(self):
        for lineNum in self.breakpoints:
            self.disable(int(lineNum))

    def enable_all(self):
        for lineNum in self.breakpoints:
            self.enable(int(lineNum))

    #adjusts breakpoint line numbers due to insertions/removals
    #TODO - this should prolly be more... generic. or placed elsewhere?
    def shift(self, added):
        newBreakpoints = {}

        #any breakpoint with a lineNum > cursorLine should be updated
        for lineNum in self.breakpoints:
            breakpoint = self.breakpoints[lineNum]

            #get the region that the marker is on
            region = self.view.get_regions(breakpoint.id)
            if region:
                #get the line number of that region
                regionLineNum = self.view.rowcol(region[0].a)[0] + 1
                printl("JsDebuggr: shifting %s to %i" % (lineNum, regionLineNum))
                #switch this breakpoint to that line number
                breakpoint.lineNum = regionLineNum
                newBreakpoints[str(regionLineNum)] = breakpoint
            else:
                printl("JsDebuggr: removing %s" % lineNum)

        #update the global breakpoint list with the new one
        self.breakpoints = newBreakpoints

    def draw_gutter_icon(self, breakpoint):
        line = self.view.line(self.view.text_point(breakpoint.lineNum - 1, 0))
        self.view.add_regions(breakpoint.id, [line], breakpoint.scope, "circle", sublime.HIDDEN | sublime.PERSISTENT)

    def clear_gutter_icon(self, id):
        self.view.erase_regions(id)


#model containing information about each breakpoint
class Breakpoint():
    def __init__(self, lineNum=0, lineText="", enabled=True, scope=BREAK_SCOPE, debugger=DEBUG_STATEMENT, condition=False):
        self.id = str(uuid.uuid4())
        self.lineNum = lineNum
        self.lineText = lineText
        self.enabled = True
        self.scope = scope
        self.debugger = debugger
        self.condition = condition

        if self.condition:
            self.set_condition(condition)

    def set_condition(self, condition):
        self.condition = condition
        self.debugger = "if(%s%s%s){%s}" % (CONDITIONAL_BEGIN_MARKER, self.condition, CONDITIONAL_END_MARKER, DEBUG_STATEMENT)
        #HACK - setting CONDITIONAL_SCOPE here is all hacksy
        self.scope = CONDITIONAL_SCOPE
        printl("JsDebuggr: conditional break: %s" % self.debugger)


# handle text commands from user
class JsDebuggr(sublime_plugin.TextCommand):

    breakpointLists = {}

    #TODO - split JsDebuggr into separate commands and
    #       use is_visible() to hide them as the context
    #       dicatates
    def is_visible(self):
        return True

    def run(self, edit, **options):
        if not should_track_view(self.view):
            printl("JsDebuggr: ignoring request as this view isn't being tracked")
            return

        breakpointList = self.get_breakpointList(self.view)

        if(options and "removeAll" in options):
            breakpointList.remove_all()
        elif(options and "toggleEnable" in options):
            self.toggle_enable_break()
        elif(options and "enableAll" in options):
            breakpointList.enable_all()
        elif(options and "disableAll" in options):
            breakpointList.disable_all()
        elif(options and "conditional" in options):
            self.add_conditional_input()
        elif(options and "editConditional" in options):
            self.edit_conditional_input()
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
            printl("JsDebuggr: creating new BreakpointList")
            self.breakpointLists[viewId] = BreakpointList(view)

        return self.breakpointLists[viewId]

    def toggle_break(self):
        breakpointList = self.get_breakpointList(self.view)

        #TODO - deal with multiple selection
        lineNum = self.get_line_nums()[0]

        breakpoint = breakpointList.get(lineNum)

        if breakpoint:
            #breakpoint exists, so turn it off.
            breakpointList.remove(lineNum)
        else:
            #else, create a new one
            breakpoint = breakpointList.add(lineNum)

    def toggle_enable_break(self):
        breakpointList = self.get_breakpointList(self.view)
        lineNum = self.get_line_nums()[0]
        breakpoint = breakpointList.get(lineNum)

        if breakpoint.enabled:
            #breakpoint is enabled, so disable it
            printl("JsDebuggr: disabling breakpoint")
            breakpointList.disable(lineNum)
        else:
            #breakpoint is disabled, so enabled it
            printl("JsDebuggr: enabling breakpoint")
            breakpointList.enable(lineNum)

    def add_conditional_input(self):
        self.view.window().show_input_panel("Enter Condition:", "", self.add_conditional, None, None)

    def add_conditional(self, text):
        breakpointList = self.get_breakpointList(self.view)
        lineNum = self.get_line_nums()[0]
        breakpointList.add(lineNum, text)

    def edit_conditional_input(self):
        breakpointList = self.get_breakpointList(self.view)
        lineNum = self.get_line_nums()[0]
        breakpoint = breakpointList.get(lineNum)
        if breakpoint.condition:
            self.view.window().show_input_panel("Enter Condition:", breakpoint.condition, self.edit_conditional, None, None)

    def edit_conditional(self, text):
        printl(text)
        breakpointList = self.get_breakpointList(self.view)
        lineNum = self.get_line_nums()[0]
        breakpoint = breakpointList.get(lineNum)
        #TODO - remove old debugger statement from document first?
        breakpoint.set_condition(text)
        #TODO - set_status probably doesn't belong here
        self.view.set_status(breakpoint.id, "JsDebuggr Condition: `%s`" % breakpoint.condition)


#write the debugger; statements to the document before save
class WriteDebug(sublime_plugin.TextCommand):
    def run(self, edit):
        #iterate breakpoints and write debugger; statments
        breakpointList = JsDebuggr.get_breakpointList(JsDebuggr, self.view)
        for id in breakpointList.breakpoints:
            breakpoint = breakpointList.breakpoints[id]
            if breakpoint.enabled:
                #TODO - find existing debugger; on this line and remove?
                #   or maybe dont even write if debugger; already exists?
                point = self.view.text_point(int(breakpoint.lineNum)-1, 0)
                self.view.insert(edit, point, breakpoint.debugger)


#remove debugger; statements from the document after save
class ClearDebug(sublime_plugin.TextCommand):
    def run(self, edit):
        breakpointList = JsDebuggr.get_breakpointList(JsDebuggr, self.view)
        for id in breakpointList.breakpoints:
            breakpoint = breakpointList.breakpoints[id]
            if breakpoint.enabled:
                line = self.view.line(self.view.text_point(breakpoint.lineNum-1, 0))
                dedebugged = self.view.substr(line)
                dedebugged = re.sub(r'%s' % re.escape(breakpoint.debugger), '', dedebugged)
                self.view.replace(edit, line, dedebugged)


#listen for events and call necessary functions
class EventListener(sublime_plugin.EventListener):

    #a dict containing the number of lines from the last update. viewId is the key
    #used to figure out if lines have been added or removed
    numLines = {}
    #kinda hacky list of breakpoint id's. when a status is added to the status bar
    #it needs to be removed later. this is a list of statuses to be removed. should
    #be emptied out pretty frequently
    setStatuses = []

    def on_modified(self, view):
        if not should_track_view(view):
            return

        viewId = str(view.id())

        #fix for https://github.com/rDr4g0n/JsDebuggr/issues/10
        if view.is_scratch():
            printl("JsDebuggr: view is marked as scratch. setting scratch to false.")
            view.set_scratch(False)

        #if the number of lines hasn't been recorded, then on_load must
        #not have been triggered, so trigger it
        if not viewId in self.numLines:
            printl("JsDebuggr: on_load wasn't fired. firing it.")
            self.on_load(view)
            if not should_track_view(view):
                return

        breakpointList = JsDebuggr.get_breakpointList(JsDebuggr, view)

        #determine how many lines are in this view
        currNumLines = view.rowcol(view.size())[0] + 1
        # if it doesnt match numLines, evaluate where the lines were inserted/removed
        if currNumLines != self.numLines[viewId]:
            added = currNumLines - self.numLines[viewId]
            printl("JsDebuggr: omg %i lines added!" % added)
            #use the cursor position to guess where the lines were inserted/removed
            #NOTE - this only supports single cursor operations
            #cursorLine = view.rowcol(view.sel()[0].a)[0] + 1
            #TODO - shift method might need a refactor/rename
            breakpointList.shift(added)

            #update new number of lines
            self.numLines[viewId] = currNumLines

    def on_pre_save(self, view):
        if not should_track_view(view):
            return

        #insert debugger; statments
        printl("JsDebuggr: inserting debuggers")
        view.run_command("write_debug")

    def on_post_save(self, view):
        if not should_track_view(view):
            #the filename may have changed, so this view may need
            #to be tracked
            if should_track_view(view, True):
                self.on_load(view)
            return

        printl("JsDebuggr: clearing debuggers")
        view.run_command("clear_debug")
        #fix for https://github.com/rDr4g0n/JsDebuggr/issues/10
        printl("JsDebuggr: marking view as scratch")
        view.set_scratch(True)

    def on_load(self, view):
        if not should_track_view(view):
            return

        viewId = str(view.id())

        #if the number of lines has not been recorded, record it
        if not viewId in self.numLines:
            self.numLines[viewId] = view.rowcol(view.size())[0] + 1
            printl("JsDebuggr: setting numlines to %i" % self.numLines[viewId])
        #force create breakpoint list

        breakpointList = JsDebuggr.get_breakpointList(JsDebuggr, view)

        if AUTOSCAN_ON_LOAD:
            #scan the doc for debugger; statements. if found, make em into
            #breakpoints and remove the statement
            existingDebuggers = view.find_all(r'%s' % re.escape(DEBUG_STATEMENT))
            printl("JsDebuggr: found %i existing debugger statements" % len(existingDebuggers))
            for region in existingDebuggers:
                condition = None
                #TODO - this whole conditional check is very ugly and hacky. there
                #       has to be a smarter way to do it... prolly a simple regex lawl
                lineText = view.substr(view.line(region))
                conditionalBegin = re.search(r'%s' % re.escape(CONDITIONAL_BEGIN_MARKER), lineText)
                if conditionalBegin:
                    #this is a conditional break, so get the condition
                    conditionalEnd = re.search(r'%s' % re.escape(CONDITIONAL_END_MARKER), lineText)
                    condition = lineText[conditionalBegin.end(0): conditionalEnd.start(0)]
                    printl("JsDebuggr: existing debugger is a conditional: '%s'" % condition)

                breakpointList.add(view.rowcol(region.a)[0] + 1, condition)

            #clear any debugger; statements from the doc
            view.run_command("clear_debug")

    def on_selection_modified(self, view):
        if not should_track_view(view):
            return

        breakpointList = JsDebuggr.get_breakpointList(JsDebuggr, view)
        cursorLine = view.rowcol(view.sel()[0].a)[0] + 1
        breakpoint = breakpointList.get(cursorLine)

        #TODO - if this is a breakpoint, take note so that is_visible() can
        #       determine which context menu items to show
        if breakpoint and breakpoint.condition:
            view.set_status(breakpoint.id, "JsDebuggr Condition: `%s`" % breakpoint.condition)
            self.setStatuses.append(breakpoint.id)
        else:
            #TODO - this whole setStatuses list seems kinda hacky...
            for id in self.setStatuses:
                view.erase_status(id)
            self.setStatuses = []
