import sublime
import uuid
import re
from .utils import debug, get_selected_line, get_line_num

class MissingRegionException(Exception):
    pass

class MissingBreakpointException(Exception):
    pass

DEBUGGER = ";'JSDBG';if(%s)debugger; "


class Breakpoint(object):
    """
    keeps track of a breakpoint's config, including the 
    line associated with the breakpoint
    """
    def __init__(self, view, line):
        # TODO - use beginning of line
        print("breakpoint added for line %s" % line)
        self.enabled = True
        self.id = str(uuid.uuid4())
        self.condition = None
        self.draw(view, line)

    def draw(self, view, line=None, hidden=False):
        # if no line was provided, try to use
        # the existing breakpoint region as the
        # line to draw at 
        if line is None:
            # TODO - catch MissingRegionException?
            line = self.getIcon(view)
            self.clear(view)

        # enabled, no conditional
        color = "keyword"
        # if disabled
        if self.enabled == False:
            color = "comment"
        # if conditional
        elif self.condition is not None:
            color = "string"
        # hidden beats all
        if hidden:
            color = ""
        view.add_regions(self.id, [line], color, "circle", sublime.HIDDEN | sublime.PERSISTENT)

    def clear(self, view):
        view.erase_regions(self.id)

    def getIcon(self, view):
        regions = view.get_regions(self.id)
        if not len(regions):
            raise MissingRegionException()
        return regions[0]

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def edit(self, condition):
        # TODO - dynamically load the enabled/disabled conditions
        # dont allow the enabled/disabled conditions
        if condition != "true" and condition != "false":
            self.condition = condition

    def getWritableCondition(self):
        """
        returns a string for writing into the
        conditional part of the debugger statement
        """

        if not self.enabled:
            # if not enabled, set condition to
            # false, so debugger will never be hit
            return "false"
        if self.condition is None:
            # if enabled but no condition is
            # present, return true
            return "true"
        return self.condition

    def destroy(self, view):
        self.clear(view)

    def isContained(self, view, line):
        bp = None
        try:
            bp = self.getIcon(view)
        except (MissingRegionException):
            debug("Couldnt find breakpoint region... must've been undo'd from history")
            return
        return line.contains(bp)

    def write(self, view, edit):
        bp = None
        try:
            bp = self.getIcon(view)
        except (MissingRegionException):
            debug("Couldnt find breakpoint region... must've been undo'd from history")
            return
        line = view.line(bp)
        lineNum = get_line_num(view, line)
        lineText = view.substr(line)
        # get offset to first non-whitespace character
        offset = len(lineText) - len(lineText.lstrip())
        # need 0 based lineNum, so -1
        point = view.text_point(lineNum-1, offset)
        view.insert(edit, point, DEBUGGER % self.getWritableCondition())

    def unwrite(self, view, edit):
        bp = None
        try:
            bp = self.getIcon(view)
        except (MissingRegionException):
            debug("Couldnt find breakpoint region... must've been undo'd from history")
            return
        line = view.line(bp)
        lineText = view.substr(line)
        dedebugged = re.sub(r'%s' % re.escape(DEBUGGER % self.getWritableCondition()), '', lineText)
        view.replace(edit, line, dedebugged)
        pass


class BreakpointList(object):

    def __init__(self, view):
        self.view = view
        self.list = []

    def __iter__(self):
        return iter([bp for bp in self.list])

    def add(self, line):
        b = Breakpoint(self.view, line)
        self.list.append(b)
        return b

    def get(self, line):
        for b in self.list:
            if b.isContained(self.view, line):
                print("line", line, "contains bp", b.id)
                return b

    def remove(self, line):
        b = self.get(line)
        if not b:
            raise MissingBreakpointException("No breakpoint at line %s, region %s" % (get_line_num(line), line))
        b.destroy(self.view)
        self.list.remove(b)

    def edit(self, line):
        b = self.get(line)
        if not b:
            raise MissingBreakpointException("No breakpoint at line %s, region %s" % (get_line_num(line), line))
        currCondition = b.condition or ""
        def doEdit(condition):
            b.edit(condition)
            b.draw(self.view, line)
        self.view.window().show_input_panel("Enter Condition:", currCondition, doEdit, None, None)

    def removeAll(self):
        for b in self.list:
            b.destroy(self.view)
        self.list = []

    def enableAll(self):
        for b in self.list:
            b.enable()
            b.draw(self.view)

    def disableAll(self):
        for b in self.list:
            b.disable()
            b.draw(self.view)

    def enable(self, line):
        b = self.get(line)
        if not b:
            raise MissingBreakpointException("No breakpoint at line %s, region %s" % (get_line_num(line), line))
        b.enable()
        b.draw(self.view, line)

    def disable(self, line):
        b = self.get(line)
        if not b:
            raise MissingBreakpointException("No breakpoint at line %s, region %s" % (get_line_num(line), line))
        b.disable()
        b.draw(self.view, line)


class BreakpointLists(object):
    def __init__(self):
        self.lists = {}

    def get(self, view):
        l = self.lists.get(view.id(), None)
        if l:
            return l
        debug("creating bp list for view", view.id())
        l = BreakpointList(view)
        self.lists[view.id()] = l
        return l
