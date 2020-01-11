#!/usr/bin/python3
#
# Author: Luke Hartman
# Description:
#   Unfinished type checker for MyPL.
#----------------------------------------------------------------------
import token
import ast
import error
import symbol_table

class TypeChecker(ast.Visitor):
    """A MyPL type checker visitor implementation where struct types
    take the form: type_id -> {v1:t1, ..., vn:tn} and function types
    take the form: fun_id -> [[t1, t2, ..., tn,], return_type]
    """
    def __init__(self):
        # initialize the symbol table (for ids -> types)
        self.sym_table = symbol_table.SymbolTable()
        # current_type holds the type of the last expression type
        self.current_type = None
        # global env (for return)
        self.sym_table.push_environment()
        # set global return type to int
        self.sym_table.add_id('return')
        self.sym_table.set_info('return', token.INTTYPE)
        # load in built-in function types
        self.sym_table.add_id('print')
        self.sym_table.set_info('print', [[token.STRINGTYPE], token.NIL])
        self.sym_table.add_id('length')
        self.sym_table.set_info('length', [[token.STRINGTYPE], token.INTTYPE])
        self.sym_table.add_id('get')
        self.sym_table.set_info('get', [[token.INTTYPE, token.STRINGTYPE], token.STRINGTYPE])
        self.sym_table.add_id('reads')
        self.sym_table.set_info('reads', [[token.NIL], token.STRINGTYPE])
        self.sym_table.add_id('readi')
        self.sym_table.set_info('readi', [[token.NIL], token.INTTYPE])
        self.sym_table.add_id('readf')
        self.sym_table.set_info('readf', [[token.NIL], token.FLOATTYPE])   
        self.sym_table.add_id('itos')
        self.sym_table.set_info('itos', [[token.INTTYPE], token.STRINGTYPE])   
        self.sym_table.add_id('itof')
        self.sym_table.set_info('itof', [[token.INTTYPE], token.FLOATTYPE])
        self.sym_table.add_id('ftos')
        self.sym_table.set_info('ftos', [[token.FLOATTYPE], token.STRINGTYPE])

    def __error(self, msg, the_token):
        raise error.MyPLError(msg, the_token.line, the_token.column)

    def visit_stmt_list(self, stmt_list):
        # add new block (scope)
        self.sym_table.push_environment()
        for stmt in stmt_list.stmts:
            stmt.accept(self)
        # remove new block
        self.sym_table.pop_environment()

    def visit_expr_stmt(self, expr_stmt):
        expr_stmt.expr.accept(self)

    def visit_var_decl_stmt(self, var_decl):
        var_decl.var_expr.accept(self)
        expr_type = self.current_type
        var_id = var_decl.var_id
        curr_env = self.sym_table.get_env_id()

        if self.sym_table.id_exists_in_env(var_id.lexeme, curr_env):
            msg = 'variable already defined in current environment'
            self.__error(msg, var_id)

        if var_decl.var_type:
            var_decl_type = var_decl.var_type
            var_decl.var_expr.accept(self)
            var_expr_type = self.current_type
            if var_decl_type == var_expr_type:
                self.sym_table.add_id(var_decl.var_id.lexeme)
                self.sym_table.set_info(var_decl.var_id.lexeme, var_decl_type.tokentype)
            else:
                self.__error('Variable declaration type error', var_decl.var_id)
        # implicit
        else:
            var_decl.var_expr.accept(self)
            var_decl.var_type = self.current_type
            self.sym_table.add_id(var_decl.var_id.lexeme)           
            self.sym_table.set_info(var_decl.var_id.lexeme, self.current_type)

    # will need to update when I do structs
    def visit_assign_stmt(self, assign_stmt):
        assign_stmt.rhs.accept(self)
        rhs_type = self.current_type
        assign_stmt.lhs.accept(self)
        lhs_type = self.current_type
        if rhs_type != token.NIL and rhs_type != lhs_type:
            msg = 'mismatch type in assignment'
            self.__error(msg, assign_stmt.lhs.path[0])

    def visit_struct_decl_stmt(self, struct_decl):pass
    def visit_fun_decl_stmt(self, fun_decl): pass
    def visit_return_stmt(self, return_stmt): pass

    def visit_while_stmt(self, while_stmt):
        while_stmt.bool_expr.accept(self)
        self.sym_table.push_environment()
        while_stmt.stmt_list.accept(self)
        self.sym_table.pop_environment()

    def visit_if_stmt(self, if_stmt):
        if_stmt.if_part.bool_expr.accept(self)
        self.sym_table.push_environment()
        if_stmt.if_part.stmt_list.accept(self)
        self.sym_table.pop_environment()
        for eif in if_stmt.elseifs:
            eif.if_part.bool_expr.accept(self)
            self.sym_table.push_environment()
            eif.else_stmts.stmt_list.accept(self)
            self.sym_table.pop_environment()
        if if_stmt.has_else:
            if_stmt.else_stmts.accept(self)

    def visit_simple_expr(self, simple_expr):
        simple_expr.term.accept(self)

    def visit_complex_expr(self, complex_expr):
        complex_expr.first_operand.accept(self)
        ltype = self.current_type
        complex_expr.rest.accept(self)
        rtype = self.current_type
        if ltype == rtype:
            # type inference rule 2
            if complex_expr.math_rel.tokentype == token.PLUS:
                if ltype in [token.STRINGVAL, token.INTVAL, token.FLOATVAL]:
                    self.current_type = ltype
                else:
                    self.__error('cannot evaluate expression on these types', complex_expr.math_rel)

            # type inference rules 3,4,5
            elif complex_expr.math_rel.tokentype in [token.MINUS, token.MULTIPLY,   token.DIVIDE]:
                if ltype in [token.INTVAL, token.FLOATVAL]:
                    self.current_type = ltype
                else:
                    self.__error('cannot evaluate expression on these types',   complex_expr.math_rel)

            # type inference rule 6
            elif complex_expr.math_rel.tokentype == token.MODULO:
                if ltype == token.INTVAL:
                    self.current_type = ltype
                else:
                    self.__error('cannot evaluate expression on these types',   complex_expr.math_rel)
        else:
            self.__error('complex expr type error', complex_expr.math_rel)

    def visit_bool_expr(self, bool_expr):
        bool_expr.first_expr.accept(self)
        first_expr_type = self.current_type
        if bool_expr.bool_rel and bool_expr.second_expr:
            bool_expr.second_expr.accept(self)
            second_expr_type = self.current_type  
            bool_tokens = [token.EQUAL, token.LESS_THAN, token.GREATER_THAN, token.LESS_THAN_EQUAL, token.GREATER_THAN_EQUAL, token.NOT_EQUAL] 
            if bool_expr.bool_rel.tokentype in bool_tokens:
                if bool_expr.bool_rel.tokentype in [token.EQUAL, token.NOT_EQUAL]:
                    if first_expr_type == second_expr_type:
                        self.current_type = token.BOOLTYPE
                    else:
                        self.__error('boolean expression type error', bool_expr.bool_rel)
                else:
                    types = [token.INTTYPE, token.FLOATTYPE, token.BOOLTYPE, token.STRINGTYPE]
                    if first_expr_type in types and second_expr_type in types and first_expr_type == second_expr_type:
                        self.current_type = token.BOOLTYPE
                    else:
                        self.__error('boolean expression type error', bool_expr.bool_rel)
        else:
            self.current_type = token.BOOLTYPE
        if bool_expr.bool_connector and bool_expr.rest:
            left_expr_type = self.current_type
            bool_expr.rest.accept(self)
            right_expr_type = self.current_type
            if bool_expr.bool_connector.tokentype in [token.OR, token.AND]:
                if left_expr_type == token.BOOLTYPE and left_expr_type == right_expr_type:
                    self.current_type = left_expr_type
                else:
                    self.__error('boolean expression type error', bool_expr.bool_rel)
        else:
            self.current_type = token.BOOLTYPE

    # will need to update when I do structs
    def visit_lvalue(self, lval):
        # check the first id in lval.path
        var_token = lval.path[0]
        if not self.sym_table.id_exists(var_token.lexeme):
            msg = 'undefined variable "%s"' % var_token.lexeme
            self.__error(msg, var_token)
        self.current_type = self.sym_table.get_info(var_token.lexeme)

    def visit_fun_param(self, fun_param): pass

    def visit_simple_rvalue(self, simple_rvalue): 
        rvals = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL]
        if simple_rvalue.val.tokentype in rvals:
            self.current_type = simple_rvalue.val.tokentype
        else:
            self.__error('simple_rvalue error', simple_rvalue.val)

    def visit_new_rvalue(self, new_rvalue): pass
    def visit_call_rvalue(self, call_rvalue): pass

    def visit_id_rvalue(self, id_rvalue):
        if self.sym_table.id_exists(id_rvalue.path[0]):
            self.current_type = self.sym_table.get_info(id_rvalue.path[0].lexeme)
        else:
            self.__error("id rvalue used before declaration", id_rvalue.path[0])
