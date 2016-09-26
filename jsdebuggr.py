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
        #line = self.view.line(self.view.text_point(breakpoint.lineNum - 1, 0))
        view.add_regions(self.id, [self.region], "keyword", "circle", sublime.HIDDEN | sublime.PERSISTENT)
        pass

    def disable(self):
        self.disabled = True

    def enable(self):
        self.disabled = False

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
        debug("added breakpoint")
        return b

    def _get_breakpoint(self, view, line):
        """
        returns the breakpoint for the provided line
        in the provided view, or creates one if absent,
        and a bool indicating if a new breakpoint was created
        """
        breakpointList = self._get_breakpoint_list(view)
        for b in breakpointList:
            if line.contains(b.region):
                debug("found breakpoint for view %s" % view.id())
                return (b, False)
        b = self._add_breakpoint(view, line)
        debug("created breakpoint for view %s" % view.id())
        return (b, True)

    def _remove_breakpoint(self, view, b):
        b.destroy(view)
        self._get_breakpoint_list(view).remove(b)
        debug("removed breakpoint")

    def toggle(self, view, line):
        """
        removes the breakpoint at line for id, or adds
        one if one is not present
        """
        b, new = self._get_breakpoint(view, line)
        if new:
            b.draw(view)
            debug("toggled breakpoint on")
        else:
            self._remove_breakpoint(view, b)
            debug("toggled breakpoint off")


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
