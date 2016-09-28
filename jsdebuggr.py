import uuid
import sublime
import sublime_plugin

# I know theres a logging package, but st3 console
# maybe introduces another layer or smoething?
DEBUG = True
def debug(*args):
    if DEBUG:
        print("JsDebuggr:", *args)


class MissingRegionException(Exception):
    pass


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
        self.draw(view, line)

    def draw(self, view, line=None, hidden=False):
        # if no line was provided, try to use
        # the existing breakpoint region as the
        # line to draw at 
        if line is None:
            line = self.get_bp(view)
            # no line was provide and no existing breakpoint
            # region, so this aint gonna work
            if line is None:
                raise MissingRegionException()
            self.clear(view)

        # TODO - add tooltip text
        color = "keyword"
        if self.enabled == False:
            color = "comment"
        if hidden:
            color = ""
        view.add_regions(self.id, [line], color, "circle", sublime.HIDDEN | sublime.PERSISTENT)

    def clear(self, view):
        view.erase_regions(self.id)

    def get_bp(self, view):
        regions = view.get_regions(self.id)
        if regions is None:
            return None
        return regions[0]

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def destroy(self, view):
        self.clear(view)

    def isContained(self, view, line):
        return line.contains(self.get_bp(view))


class MissingBreakpointException(Exception):
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

    def removeAll(self):
        for b in self.list:
            b.destroy(self.view)

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

breakpointLists = BreakpointLists()


def get_selected_line(view):
    # TODO - multiselect
    sel = view.sel()[0]
    line = view.line(sel)
    lineNum = get_line_num(view, line)
    return (line, lineNum)

def get_line_num(view, line):
    return view.rowcol(line.a)[0] + 1


class JsDebuggrAddCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        l = breakpointLists.get(self.view)
        line, lineNum = get_selected_line(self.view)
        debug("add at", lineNum)
        l.add(line)

    def is_enabled(self):
        l = breakpointLists.get(self.view)
        line, lineNum = get_selected_line(self.view)
        b = l.get(line)
        return not b


class JsDebuggrRemoveCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        l = breakpointLists.get(self.view)
        line, lineNum = get_selected_line(self.view)
        debug("remove at", lineNum)
        # TODO - catch missing bp err
        l.remove(line)

    def is_enabled(self):
        l = breakpointLists.get(self.view)
        line, lineNum = get_selected_line(self.view)
        b = l.get(line)
        return bool(b)


class JsDebuggrRemoveAllCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        debug("remove all")
        l = breakpointLists.get(self.view)
        l.removeAll()


class JsDebuggrDisableCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        l = breakpointLists.get(self.view)
        line, lineNum = get_selected_line(self.view)
        debug("disable at ", lineNum)
        # TODO - catch missing bp err
        l.disable(line)

    def is_enabled(self):
        l = breakpointLists.get(self.view)
        line, lineNum = get_selected_line(self.view)
        b = l.get(line)
        return bool(b and b.enabled)


class JsDebuggrDisableAllCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        debug("disable all")
        l = breakpointLists.get(self.view)
        l.disableAll()


class JsDebuggrEnableAllCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        debug("enable all")
        l = breakpointLists.get(self.view)
        l.enableAll()


class JsDebuggrEnableCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        l = breakpointLists.get(self.view)
        line, lineNum = get_selected_line(self.view)
        debug("enable at", lineNum)
        l.enable(line)

    def is_enabled(self):
        l = breakpointLists.get(self.view)
        line, lineNum = get_selected_line(self.view)
        b = l.get(line)
        return bool(b and not b.enabled)



#write the debugger; statements to the document before save
class WriteDebug(sublime_plugin.TextCommand):
    def run(self, edit):
        l = breakpointLists.get(self.view)
        for b in l:
            if b.enabled:
                debug("should write bp")
                """
                line = self.view.line(b.get_bp(view))
                lineNum = get_line_num(self.view, line)
                lineText = self.view.substr(line)
                offset = len(lineText) - len(lineText.lstrip())
                point = self.view.text_point(lineNum, offset)
                self.view.insert(edit, point, ";'JsDebuggr';")
                """


class EventListener(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        debug("inserting debuggers")
        view.run_command("write_debug")
