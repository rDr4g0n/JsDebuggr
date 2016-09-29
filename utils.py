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
