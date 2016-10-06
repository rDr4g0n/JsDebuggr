# I know theres a logging package, but st3 console
# maybe introduces another layer or smoething?
DEBUG = True
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
