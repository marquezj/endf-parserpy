############################################################
#
# Author(s):       Georg Schnabel
# Email:           g.schnabel@iaea.org
# Creation date:   2024/04/21
# Last modified:   2024/04/25
# License:         MIT
# Copyright (c) 2024 International Atomic Energy Agency (IAEA)
#
############################################################

from lark.lexer import Token
from lark.tree import Tree
from endf_parserpy.compiler.expr_utils.conversion import VariableToken
from endf_parserpy.compiler.expr_utils.node_trafos import node2str
from endf_parserpy.compiler.expr_utils.node_checks import is_number
from endf_parserpy.compiler.expr_utils.exceptions import VariableMissingError
from endf_parserpy.compiler.variable_management import find_parent_dict
from .cpp_varaux import get_cpp_varname
from .cpp_type_information import (
    get_query_modules,
    get_assign_modules,
    get_vartype_modules,
)


def need_read_check(vartok, vardict, indices=None):
    if find_parent_dict(vartok, vardict) is None:
        return False
    if vartok.cpp_namespace is True:
        return False
    return True


def did_read_var(vartok, vardict, indices=None):
    if vartok.cpp_namespace is True:
        raise NotImplementedError(
            "read tracking not enabled for variables in cpp_namespace"
        )
    pardict = find_parent_dict(vartok, vardict)
    if pardict is None:
        return "false"
    idxstrs = None
    if indices is not None:
        idxstrs = []
        for i, idxtok in enumerate(vartok.indices):
            idxstrs.append(get_idxstr(vartok, i, vardict))
    for query in get_query_modules():
        if query.is_responsible(vartok, vardict):
            return query.did_read_var(vartok, vardict, idxstrs)
    raise TypeError(f"{vartok} has unknown type")


def get_cpp_extvarname(vartok, vardict):
    if find_parent_dict(vartok, vardict) is None:
        raise VariableMissingError(f"variable {vartok} missing/not encountered")
    varname = get_cpp_varname(vartok)
    idxstrs = []
    for i, idxtok in enumerate(vartok.indices):
        idxstrs.append(get_idxstr(vartok, i, vardict))
    for query in get_query_modules():
        if query.is_responsible(vartok, vardict):
            return query.assemble_extvarname(varname, idxstrs)
    raise TypeError(f"{vartok} has unknown datatype")


def get_cpp_objstr(tok, vardict):
    if isinstance(tok, VariableToken):
        return get_cpp_extvarname(tok, vardict)
    elif is_number(tok):
        varname = str(tok)
        return varname
    raise NotImplementedError("evil programmer, what did you do?")


def get_idxstr(vartok, i, vardict):
    idxtok = vartok.indices[i]
    cpp_idxstr = get_cpp_objstr(idxtok, vardict)
    return cpp_idxstr


def logical_expr2cppstr(node, vardict):
    if isinstance(node, VariableToken):
        return get_cpp_extvarname(node, vardict)
    elif isinstance(node, Token):
        if node == "and":
            return "&&"
        elif node == "or":
            return "||"
        else:
            return str(node)
    elif isinstance(node, Tree):
        return (
            "(" + "".join(logical_expr2cppstr(c, vardict) for c in node.children) + ")"
        )
    raise NotImplementedError("should not happen")


def expr2str_shiftidx(node, vardict, rawvars=False):
    if not isinstance(node, VariableToken):
        return node2str(node)
    if rawvars in (True, False):
        use_cpp_name = not rawvars
    else:
        use_cpp_name = node not in rawvars
    if use_cpp_name:
        varname = get_cpp_extvarname(node, vardict)
    else:
        varname = str(node)
    return varname