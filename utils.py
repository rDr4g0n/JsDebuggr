# I know theres a logging package, but st3 console
# maybe introduces another layer or smoething?
DEBUG = False
def debug(*args):
    if DEBUG:
        print("JsDebuggr:", *args)

def get_selected_line(view):
    # TODO - multiselect
    sel = view.sel()[0]
    line = view.line(sel)
    lineNum = get_line_num(view, line)
    return (line, lineNum)

def get_line_num(view, line):
    return view.rowcol(line.a)[0] + 1
    
def get_current_syntax(view, settings):
    # TODO - this seems like its just waitin to asplode
    currSyntax = view.settings().get("syntax").split("/")[-1]
    debug("current syntax is %s" % currSyntax)
    languages = settings.get("languages")
    # TODO - one day become a real grown python
    # developer and turn this into an
    # impenetrable one-liner
    for l in languages:
        for s in l["syntaxes"]:
            if s == currSyntax:
                return l
    return None

def should_track(view):
    return view.settings().get("language", None) is not None

def is_valid_scope(view):
    """
    checks selection in given view to determine
    scope and compares against supported scopes
    defined for this language
    """
    if not should_track(view):
        return False
    language = view.settings().get("language", None)
    supported_scopes = language.get("scopes")
    # if no scopes are specified, any point is ok
    if len(supported_scopes) == 0:
        return True
    # NOTE - only gets scope of first selection
    scope = view.scope_name(view.sel()[0].a).split()
    matching = [s for s in supported_scopes if s in scope]
    if len(matching) > 0:
        return True
    return False

def if_valid_scope(fn):
    def wrapper(*args, **kwargs):
        # NOTE: assumes first arg is 
        # self for a BreakpointList
        # TODO - make safer
        if is_valid_scope(args[0].view):
            return fn(*args, **kwargs)
        return False
    return wrapper

def if_should_track(fn):
    def wrapper(*args, **kwargs):
        # NOTE: assumes first arg is 
        # self for a BreakpointList
        # TODO - make safer
        if should_track(args[0].view):
            return fn(*args, **kwargs)
        return False
    return wrapper
