#!/usr/bin/python3
#
# Author: Luke Hartman
# Description:
#   MyPL interpreter without funcitons, structs, and type checking.
#----------------------------------------------------------------------
import ast
import token as token
import error as error
import symbol_table as sym_tbl

class Interpreter(ast.Visitor):
    """A MyPL interpreter visitor implementation"""

    def __init__(self):
        # initialize the symbol table (for ids -> values)
        self.sym_table = sym_tbl.SymbolTable()
        # holds the type of last expression type
        self.current_value = None
        # the heap {oid:struct_obj}
        self.heap = {}

    def __error(self, msg, the_token):
        raise error.MyPLError(msg, the_token.line, the_token.column)

    def visit_stmt_list(self, stmt_list):
        self.sym_table.push_environment()
        for stmt in stmt_list.stmts:
            stmt.accept(self)
        self.sym_table.pop_environment()

    def visit_id_rvalue(self, id_rvalue):
        var_name = id_rvalue.path[0].lexeme
        var_val = self.sym_table.get_info(var_name)
        for path_id in id_rvalue.path[1:]:
            print(path_id) # hw7
            #... handle path expressions ...
        self.current_value = var_val

    def visit_lvalue(self, lval):
        identifier = lval.path[0].lexeme
        if len(lval.path) == 1:
            self.sym_table.set_info(identifier, self.current_value)
        else:
            pass # hw7

    def visit_var_decl_stmt(self, var_decl):
        var_decl.var_expr.accept(self)
        exp_value = self.current_value
        var_name = var_decl.var_id.lexeme
        self.sym_table.add_id(var_name)
        self.sym_table.set_info(var_name, exp_value)

    def visit_call_rvalue(self, call_rvalue):
        # handle built in functions first
        built_ins = ['print', 'length', 'get', 'readi', 'reads',
                     'readf', 'itof', 'itos', 'ftos', 'stoi', 'stof']
        if call_rvalue.fun.lexeme in built_ins:
            self.__built_in_fun_helper(call_rvalue)
        else:
            # user-defined fxn calls
            pass

    # Basic structure of the built-in function call helper
    def __built_in_fun_helper(self, call_rvalue):
        fun_name = call_rvalue.fun.lexeme
        arg_vals = []
        for arg in call_rvalue.args:
            arg.accept(self)
            arg_vals.append(self.current_value)

        #... evaluate each call argument and store in arg_vals ...
        # check for nil values
        for arg in enumerate(arg_vals):
            if arg is None:
                # ... report a nil value error ...
                self.__error('bad value: should not be nil', call_rvalue.fun)

            # perform each function
            if fun_name == 'print':
                arg_vals[0] = str(arg_vals[0])
                arg_vals[0] = arg_vals[0].replace('\\n','\n')
                print(arg_vals[0], end='')
            elif fun_name == 'length':
                self.current_value = len(arg_vals[0])
            elif fun_name == 'get':
                if 0 <= arg_vals[0] < len(arg_vals[1]):
                    self.current_value = arg_vals[1][arg_vals[0]]
                else:
                    self.__error('Index of range', call_rvalue.fun)
            elif fun_name == 'itof':
                try:
                    self.current_value == float(arg_vals[0])
                except:
                    self.__error('bad argument: should be an int', call_rvalue.fun)
            elif fun_name == 'itos':
                try:
                    self.current_value == str(arg_vals[0])
                except:
                    self.__error('bad argument: should be an int', call_rvalue.fun)
            elif fun_name == 'stoi':
                try:
                    self.current_value == int(arg_vals[0])
                except:
                    self.__error('bad argument: should be a string', call_rvalue.fun)
            elif fun_name == 'stof':
                try:
                    self.current_value == float(arg_vals[0])
                except:
                    self.__error('bad argument: should be a string', call_rvalue.fun)
        # functions without arguments    
        if fun_name == 'reads':
            try:
                self.current_value = str(input())
            except ValueError:
                self.__error('bad string', call_rvalue.fun)
        elif fun_name == 'readi':
            try:
                self.current_value = int(input())
            except ValueError:
                self.__error('bad int value', call_rvalue.fun)
        elif fun_name == 'readf':
            try:
                self.current_value = float(input())
            except ValueError:
                self.__error('bad float value', call_rvalue.fun)    

    def visit_expr_stmt(self, expr_stmt):
        expr_stmt.expr.accept(self)

    def visit_assign_stmt(self, assign_stmt): 
        assign_stmt.rhs.accept(self)
        self.sym_table.set_info(assign_stmt.lhs.path[0].lexeme, self.current_value) 

    def visit_while_stmt(self, while_stmt):
        self.sym_table.push_environment()
        while_stmt.bool_expr.accept(self)
        while self.current_value:
            for stmt in while_stmt.stmt_list.stmts:
                stmt.accept(self)
            while_stmt.bool_expr.accept(self)
        self.sym_table.pop_environment()

    def visit_if_stmt(self, if_stmt):
        if_stmt.if_part.bool_expr.accept(self)
        if self.current_value:
            self.sym_table.push_environment()
            if_stmt.if_part.stmt_list.accept(self)
            self.sym_table.pop_environment()
            return
        for elseif in if_stmt.elseifs:
            elseif.bool_expr.accept(self)
            if self.current_value:
                self.sym_table.push_environment()
                elseif.stmt_list.accept(self)
                self.sym_table.pop_environment()
                return
        if if_stmt.has_else:
            self.sym_table.push_environment()
            if_stmt.else_stmts.accept(self)
            self.sym_table.pop_environment()
            return


    def visit_simple_expr(self, simple_expr):
        simple_expr.term.accept(self)

    def visit_complex_expr(self, complex_expr):
        complex_expr.first_operand.accept(self)
        first_val = self.current_value
        complex_expr.rest.accept(self)
        second_val = self.current_value
        mathrel = complex_expr.math_rel

        # because I don't have my type checker
        if isinstance(first_val, str) or isinstance(second_val, str):
            first_val = str(first_val)
            second_val = str(second_val)

        # [token.PLUS, token.MINUS, token.DIVIDE, token.MULTIPLY, token.MODULO]
        if mathrel.tokentype == token.PLUS:
            self.current_value = first_val + second_val
        elif mathrel.tokentype == token.MINUS:
            self.current_value = first_val - second_val
        elif mathrel.tokentype == token.DIVIDE:
            self.current_value = first_val / second_val
        elif mathrel.tokentype == token.MULTIPLY:
            self.current_value = first_val * second_val
        elif mathrel.tokentype == token.MODULO:
            self.current_value = first_val % second_val

    def visit_bool_expr(self, bool_expr):
        bool_expr.first_expr.accept(self)
        first_expr_val = self.current_value
        # [token.EQUAL, token.LESS_THAN, token.GREATER_THAN, token.LESS_THAN_EQUAL, token.GREATER_THAN_EQUAL, token.NOT_EQUAL]
        if bool_expr.bool_rel:
            bool_expr.second_expr.accept(self)
            second_expr_val = self.current_value
            if bool_expr.bool_rel.tokentype == token.EQUAL:
                self.current_value = (first_expr_val == second_expr_val)
            elif bool_expr.bool_rel.tokentype == token.LESS_THAN:
                self.current_value = (first_expr_val < second_expr_val)
            elif bool_expr.bool_rel.tokentype == token.GREATER_THAN:
                self.current_value = (first_expr_val > second_expr_val)
            elif bool_expr.bool_rel.tokentype == token.LESS_THAN_EQUAL:
                self.current_value = (first_expr_val <= second_expr_val)
            elif bool_expr.bool_rel.tokentype == token.GREATER_THAN_EQUAL:
                self.current_value = (first_expr_val >= second_expr_val)
            elif bool_expr.bool_rel.tokentype == token.NOT_EQUAL:
                self.current_value = (first_expr_val != second_expr_val)


    
    def visit_simple_rvalue(self, simple_rvalue):
        #rvals = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL]
        rval_type = simple_rvalue.val.tokentype
        rval_lexeme = simple_rvalue.val.lexeme
        if rval_type == token.STRINGVAL:
            self.current_value = rval_lexeme
        elif rval_type == token.INTVAL:
            self.current_value = int(rval_lexeme)
        elif rval_type == token.BOOLVAL:
            if rval_lexeme == 'true':
                self.current_value = True
            else:
                self.current_value = False
        elif rval_type == token.FLOATVAL:
            self.current_value = float(rval_lexeme)
        elif rval_type == token.NIL:
            self.current_value = None
    
    # hw7
    def visit_struct_decl_stmt(self, struct_decl):
        struct_decl.accept(self)

    def visit_fun_decl_stmt(self, fun_decl): pass
    def visit_return_stmt(self, return_stmt): pass
    def visit_new_rvalue(self, new_rvalue): pass
    def visit_fun_param(self, fun_param): pass
