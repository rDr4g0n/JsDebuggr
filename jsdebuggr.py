import sublime
import sublime_plugin
import uuid

# I know theres a logging package, but st3 console
# maybe introduces another layer or smoething?
DEBUG = True
def debug(*args):
    if DEBUG:
        print("JsDebuggr:", *args)

def get_line_num(view, line):
    view.rowcol(s.a) + 1


class Breakpoint(object):
    """
    keeps track of a breakpoint's config, including the 
    region associated with the breakpoint
    """
    def __init__(self, region):
        # TODO - use beginning of region
        self.region = region
        self.enabled = True
        self.id = str(uuid.uuid4())

    def draw(self, view):
        # TODO - add marker
        # TODO - add tooltip text
        color = "keyword"
        if self.enabled == False:
            color = "comment"
        view.add_regions(self.id, [self.region], color, "circle", sublime.HIDDEN | sublime.PERSISTENT)
        pass

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def destroy(self, view):
        view.erase_regions(self.id)
        pass


class BreakpointLists(object):
    """ collections of breakpoints, by view id """
    def __init__(self):
        self.breakpointLists = {}

    def _get_breakpoint_list(self, view):
        """
        gets a breakpoint list for a view with the given id,
        or creates a list if absent
        """
        breakpointList = self.breakpointLists.get(view.id(), None)
        if not breakpointList:
            self.breakpointLists[view.id()] = []
        return self.breakpointLists[view.id()]

    def _add_breakpoint(self, view, line):
        breakpointList = self._get_breakpoint_list(view)
        b = Breakpoint(line)
        breakpointList.append(b)
        return b

    def get_breakpoint(self, view, line, create=False):
        breakpointList = self._get_breakpoint_list(view)
        for b in breakpointList:
            if line.contains(b.region):
                return (b, True)
        if(create):
            b = self._add_breakpoint(view, line)
            return (b, False)
        return (False, False)

    def _remove_breakpoint(self, view, b):
        b.destroy(view)
        self._get_breakpoint_list(view).remove(b)

    def toggle(self, view, line):
        """
        removes the breakpoint at line for id, or adds
        one if one is not present
        """
        b, exists = self.get_breakpoint(view, line, create=True)
        if exists:
            self._remove_breakpoint(view, b)
        else:
            b.draw(view)

    def removeAll(self, view):
        for b in self._get_breakpoint_list(view):
            b.destroy(view)
        del self.breakpointLists[view.id()]

    def enableAll(self, view):
        for b in self._get_breakpoint_list(view):
            b.enable()
            b.draw(view)

    def disableAll(self, view):
        for b in self._get_breakpoint_list(view):
            b.disable()
            b.draw(view)

    def enable(self, view, line):
        b, exists = self.get_breakpoint(view, line, create=True)
        if exists:
            b.enable()
            b.draw(view)

    def disable(self, view, line):
        b, exists = self.get_breakpoint(view, line, create=True)
        if exists:
            b.disable()
            b.draw(view)


breakpointLists = BreakpointLists()

class JsDebuggrCommand(sublime_plugin.TextCommand):
    def run(self, edit, **options):
        # TODO - other commands based on options
        debug("run")
        self.toggle_breakpoint()

    def toggle_breakpoint(self):
        #TODO - multiple selection
        debug("toggle")
        sel = self.view.sel()[0]
        line = self.view.line(sel)
        breakpointLists.toggle(self.view, line)

class JsDebuggrAddCommand(sublime_plugin.TextCommand):
    def run(self, view, **args):
        debug("add")
        sel = self.view.sel()[0]
        line = self.view.line(sel)
        breakpointLists.toggle(self.view, line)

    def is_enabled(self):
        sel = self.view.sel()[0]
        line = self.view.line(sel)
        _, exists = breakpointLists.get_breakpoint(self.view, line)
        return not exists

class JsDebuggrRemoveCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        debug("add")
        sel = self.view.sel()[0]
        line = self.view.line(sel)
        breakpointLists.toggle(self.view, line)

    def is_enabled(self):
        sel = self.view.sel()[0]
        line = self.view.line(sel)
        _, exists = breakpointLists.get_breakpoint(self.view, line)
        return exists


class JsDebuggrRemoveAllCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        debug("remove all")
        breakpointLists.removeAll(self.view)


class JsDebuggrDisableCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        debug("disable")
        sel = self.view.sel()[0]
        line = self.view.line(sel)
        breakpointLists.disable(self.view, line)

    def is_enabled(self):
        sel = self.view.sel()[0]
        line = self.view.line(sel)
        b, _ = breakpointLists.get_breakpoint(self.view, line)
        return b and b.enabled


class JsDebuggrDisableAllCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        debug("disable all")
        breakpointLists.disableAll(self.view)


class JsDebuggrEnableAllCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        debug("enable all")
        breakpointLists.enableAll(self.view)


class JsDebuggrEnableCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        debug("enable")
        sel = self.view.sel()[0]
        line = self.view.line(sel)
        breakpointLists.enable(self.view, line)

    def is_enabled(self):
        sel = self.view.sel()[0]
        line = self.view.line(sel)
        b, _ = breakpointLists.get_breakpoint(self.view, line)
        return b and not b.enabled
