import sublime
import sublime_plugin
from .breakpoint import Breakpoint, BreakpointList, BreakpointLists, MissingRegionException, MissingBreakpointException, DEBUGGER
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


class JsDebuggrEditCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        l = breakpointLists.get(self.view)
        line, lineNum = get_selected_line(self.view)
        debug("edit at", lineNum)
        # TODO - catch missing bp err
        l.edit(line)

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
    # keep track of visible statuses so
    # they can be cleared on selection change
    # TODO - not really great :/
    setStatuses = []

    def on_pre_save(self, view):
        debug("inserting debuggers")
        view.run_command("write_debug")

    def on_post_save(self, view):
        debug("removing debuggers")
        view.run_command("un_write_debug")
        # setting view to scratch prevents the "unsaved changes"
        # warning when closing a file whos only changes are
        # adding/removing debuggers
        debug("marking view as scratch")
        view.set_scratch(True)

    def on_modified(self, view):
        # TODO - will this incorrectly set actual scratch views
        # to not scratch?
        if view.is_scratch():
            debug("view is marked as scratch. setting scratch to false.")
            view.set_scratch(False)

    def on_selection_modified(self, view):        
        l = breakpointLists.get(view)
        line, lineNum = get_selected_line(view)
        b = l.get(line)

        # TODO - multiple cursors?
        if b and b.condition is not None:
            view.set_status(b.id, "JsDebuggr Condition: %s" % b.condition)
            self.setStatuses.append(b.id)
        else:
            for id in self.setStatuses:
                view.erase_status(id)
            self.setStatuses = []

    def on_load(self, view):
        # TODO - use DEBUGGER var
        existingDebuggers = view.find_all(";'JSDBG';if(.*)debugger;")
        debug("found %i existing debugger statements" % len(existingDebuggers))
        debug("%s" % existingDebuggers)
        for d in existingDebuggers:
            pass

            # TODO - extract condition
            # TODO - delete debugger text
            # TODO - create breakpoints
