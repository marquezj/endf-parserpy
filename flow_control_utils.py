from tree_utils import get_child, get_child_value


def cycle_for_loop(tree, tree_handler, datadic, loop_vars):
    assert tree.data == 'for_loop'
    for_head = get_child(tree, 'for_head')
    varname = get_child_value(for_head, 'VARNAME')
    start = int(get_child_value(for_head, 'FOR_START'))
    stop = int(get_child_value(for_head, 'FOR_STOP'))
    for_body = get_child(tree, 'for_body')
    assert varname not in  loop_vars
    for i in range(start, stop+1):
        loop_vars[varname] = i 
        tree_handler(for_body)
    del(loop_vars[varname])

