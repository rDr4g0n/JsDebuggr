import re
import sublime
import sublime_plugin
from .breakpoint import Breakpoint, BreakpointList, BreakpointLists, MissingRegionException, MissingBreakpointException
from .utils import debug, get_selected_line, get_line_num, get_current_syntax, should_track

breakpointLists = BreakpointLists()
# TODO - break languages out into its own thingy
settings = sublime.load_settings("jsdebuggr.sublime-settings")

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


class JsDebuggrToggleCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        l = breakpointLists.get(self.view)
        line, lineNum = get_selected_line(self.view)
        debug("toggle at", lineNum)
        b = l.get(line)
        if b:
            l.remove(line)
        else:
            l.add(line)


class JsDebuggrToggleEditCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        l = breakpointLists.get(self.view)
        line, lineNum = get_selected_line(self.view)
        debug("toggle at", lineNum)
        b = l.get(line)
        if not b:
            l.add(line)
        l.edit(line)


class JsDebuggrToggleEnableCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        l = breakpointLists.get(self.view)
        line, lineNum = get_selected_line(self.view)
        debug("toggle enable at", lineNum)
        b = l.get(line)
        if b and b.enabled:
            l.disable(line)
        elif b and not b.enabled:
            l.enable(line)


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

# a lil hack to get an edit context from inside a view
class RemoveDebug(sublime_plugin.TextCommand):
    def run(self, edit, a, b):
        region = sublime.Region(a,b)
        self.view.erase(edit, region)


class EventListener(sublime_plugin.EventListener):
    # keep track of visible statuses so
    # they can be cleared on selection change
    # TODO - not really great :/
    setStatuses = []

    def on_load(self, view):
        syntax = get_current_syntax(view, settings)
        if syntax is None:
            debug("aint gonna bother with %s, I don't have a matching syntax" % view.file_name())
            return

        viewSettings = view.settings()
        viewSettings.set("language", syntax)
        viewSettings.set("debugger", syntax["debugger"])
        viewSettings.set("debuggerRegex", syntax["debuggerRegex"])
        viewSettings.set("enabled", syntax["enabled"])
        viewSettings.set("disabled", syntax["disabled"])
        viewSettings.set("scopes", syntax["scopes"])

        debuggerRe = viewSettings.get("debuggerRegex")
        existingDebuggers = view.find_all(debuggerRe)
        debug("found %i existing debugger statements" % len(existingDebuggers))

        l = breakpointLists.get(view)

        for d in existingDebuggers:
            string = view.substr(d)
            reMatch = re.match(debuggerRe, string);
            condition = None
            if reMatch:
                condition = reMatch.group(1)
            lineNum = get_line_num(view, d)
            debug("found debug at", lineNum, "with condition", condition)
            b = l.add(d)

            # TODO - this is very internals-y, probably
            # breaking an abstraction
            if condition == syntax["disabled"]:
                b.disable()
            b.edit(condition)
            b.draw(view)

        # delete the debugger statements now that the
        # breakpoints have been created
        for d in existingDebuggers:
            view.run_command("remove_debug", {"a": d.a, "b": d.b})

        # were editing the view, but dont want it to
        # be marked dirty, so mark it as scratch
        debug("marking view as scratch")
        view.set_scratch(True)

    def on_pre_save(self, view):
        if not should_track(view):
            return
        debug("inserting debuggers")
        view.run_command("write_debug")

    def on_post_save(self, view):
        if not should_track(view):
            return
        debug("removing debuggers")
        view.run_command("un_write_debug")
        # setting view to scratch prevents the "unsaved changes"
        # warning when closing a file whos only changes are
        # adding/removing debuggers
        debug("marking view as scratch")
        view.set_scratch(True)

    def on_modified(self, view):
        if not should_track(view):
            return
        # TODO - will this incorrectly set actual scratch views
        # to not scratch?
        if view.is_scratch():
            debug("view is marked as scratch. setting scratch to false.")
            view.set_scratch(False)

    def on_selection_modified(self, view):
        if not should_track(view):
            return
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
