import sublime
import sublime_plugin
from .breakpoint import Breakpoint, BreakpointList, BreakpointLists, MissingRegionException, MissingBreakpointException
from .utils import debug, get_selected_line, get_line_num

breakpointLists = BreakpointLists()

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
            b.write(self.view, edit)

class UnWriteDebug(sublime_plugin.TextCommand):
    def run(self, edit):
        l = breakpointLists.get(self.view)
        for b in l:
            b.unwrite(self.view, edit)


class EventListener(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        debug("inserting debuggers")
        view.run_command("write_debug")

    def on_post_save(self, view):
        debug("removing debuggers")
        view.run_command("un_write_debug")
