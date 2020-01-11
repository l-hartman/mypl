# Author: Luke Hartman
# Course: CPSC 326 - 01, Spring 2019
# Assignment: 4
# Description:
#   This class parses tokens acccording to MyPL grammar
#   using recursive descent and also builds an AST. 
import error
import lexer
import token
import ast

# This class pulls tokens from the lexer class one-by-one and checks
# each token against MyPL grammer while created an AST.
class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None

    def parse(self):
        """succeeds if program is syntactically well-formed."""
        self.__advance()
        stmt_list_node = self.__stmts(ast.StmtList())
        self.__eat(token.EOS)
        return stmt_list_node

    def __advance(self):
        """grab the next token from the lexer"""    
        self.current_token = self.lexer.next_token()

    def __eat(self, tokentype):
        """compare current token with token type"""
        if self.current_token.tokentype == tokentype:
            self.__advance()
        else:
            self.__error([tokentype])

    def __error(self, expected_tokens):
        """function that raises MyPLErrors"""
        s = "expecting " + " or ".join(expected_tokens) + ', found "' + self.current_token.lexeme + '" in parser'
        l = self.current_token.line
        c = self.current_token.column
        raise error.MyPLError(s, l, c)

    def __check_tokentype(self, token):
        """a function to compare the current token with a token argument"""
        if self.current_token.tokentype == token:
            return True
        else:
            return False

    # Beginning of recursive descent functions
    def __stmts(self, stmt_list_node):
        """<stmts> ::= <stmt> <stmts> | e"""
        if not self.__check_tokentype(token.EOS):
            stmt_list_node.stmts.append(self.__stmt())
            self.__stmts(stmt_list_node)
        return stmt_list_node

    def __bstmts(self, stmt_list_node):
        possible_tokens = [token.VAR, token.SET, token.IF, token.WHILE, token.RETURN, token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL, token.NEW, token.ID, token.LPAREN]
        if self.current_token.tokentype in possible_tokens:
            stmt_list_node.stmts.append(self.__bstmt())
            stmt_list_node = self.__bstmts(stmt_list_node)
        return stmt_list_node

    def __stmt(self):
        """<stmt> ::= <sdecl> | <fdecl> | <bstmt>"""
        if self.__check_tokentype(token.STRUCTTYPE):
            return self.__sdecl()
        elif self.__check_tokentype(token.FUN):
            return self.__fdecl()
        else:
            return self.__bstmt()

    def __bstmt(self):
        if self.__check_tokentype(token.VAR):
            return self.__vdecl()
        elif self.__check_tokentype(token.SET):
            return self.__assign()
        elif self.__check_tokentype(token.IF):
            return self.__cond()
        elif self.__check_tokentype(token.WHILE):
            return self.__while()
        elif self.__check_tokentype(token.RETURN):
            return self.__exit()
        else:
            expr_stmt_node = ast.ExprStmt()
            expr_stmt_node.expr = self.__expr()
            self.__eat(token.SEMICOLON)
            return expr_stmt_node

    def __sdecl(self):
        self.__eat(token.STRUCTTYPE)
        sdecl_stmt_node = ast.StructDeclStmt()
        sdecl_stmt_node.struct_id = self.current_token
        self.__eat(token.ID)
        sdecl_stmt_node.var_decls = self.__vdecls([])
        self.__eat(token.END)
        return sdecl_stmt_node

    def __vdecls(self, vdecl_list):
        if self.__check_tokentype(token.VAR):
            vdecl_list.append(self.__vdecl())
            self.__vdecls(vdecl_list)
        return vdecl_list

    def __fdecl(self):
        self.__eat(token.FUN)
        fdecl_stmt_node = ast.FunDeclStmt()
        fdecl_stmt_node.return_type = self.current_token
        if self.__check_tokentype(token.NIL):
            self.__advance()
        else:
            self.__type()
        fdecl_stmt_node.fun_name = self.current_token
        self.__eat(token.ID)
        self.__eat(token.LPAREN)
        fdecl_stmt_node.params = self.__params()
        self.__eat(token.RPAREN)
        fdecl_stmt_node.stmt_list = self.__bstmts(ast.StmtList())
        self.__eat(token.END)
        return fdecl_stmt_node

    def __params(self):
        # todo: make this function return param list
        params = []
        if self.__check_tokentype(token.ID):
            param = ast.FunParam()
            param.param_name = self.current_token
            self.__advance()
            self.__eat(token.COLON)
            param.param_type = self.__type()
            params.append(param)
            while self.__check_tokentype(token.COMMA):
                self.__advance()
                param = ast.FunParam()
                param.param_name = self.current_token
                self.__eat(token.ID)
                self.__eat(token.COLON)
                param.param_type = self.__type()
        return params

    def __type(self):
        curr_token = self.current_token 
        types = [token.ID, token.INTTYPE, token.FLOATTYPE, token.BOOLTYPE, token.STRINGTYPE]
        if curr_token.tokentype in types:
            self.__advance()
            return curr_token 
        else:
            self.__error(types)

    def __exit(self):
        return_stmt_node = ast.ReturnStmt()
        return_stmt_node.return_token = self.current_token
        self.__advance()
        possible_tokens = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL, token.NEW, token.ID, token.LPAREN]
        curr_token = self.current_token.tokentype
        if curr_token in possible_tokens:
            return_stmt_node.return_expr = self.__expr()
        # return; ???
        self.__eat(token.SEMICOLON)
        return return_stmt_node

    def __vdecl(self):
        self.__eat(token.VAR)
        vdecl_stmt_node = ast.VarDeclStmt()
        vdecl_stmt_node.var_id = self.current_token
        self.__eat(token.ID)
        vdecl_stmt_node.var_type = self.__tdecl()
        self.__eat(token.ASSIGN)
        vdecl_stmt_node.var_expr = self.__expr()
        self.__eat(token.SEMICOLON)
        return vdecl_stmt_node

    def __tdecl(self):
        if self.__check_tokentype(token.COLON):
            self.__advance()
            return self.__type()
        return None

    def __assign(self):
        self.__eat(token.SET)
        assign_stmt_node = ast.AssignStmt()
        assign_stmt_node.lhs = self.__lvalue()
        self.__eat(token.ASSIGN)
        assign_stmt_node.rhs = self.__expr()
        self.__eat(token.SEMICOLON)
        return assign_stmt_node

    def __lvalue(self):
        lvalue_node = ast.LValue()
        lvalue_node.path.append(self.current_token)
        self.__eat(token.ID)
        while self.__check_tokentype(token.DOT):
            self.__advance()
            lvalue_node.path.append(self.current_token)
            self.__eat(token.ID)
        return lvalue_node

    def __cond(self):
        if_stmt_node = ast.IfStmt()
        self.__eat(token.IF)
        if_stmt_node.if_part.bool_expr = self.__bexpr()
        self.__eat(token.THEN)
        if_stmt_node.if_part.stmt_list = self.__bstmts(ast.StmtList())
        if_stmt_node = self.__condt(if_stmt_node)
        self.__eat(token.END)
        return if_stmt_node

    def __condt(self, if_stmt_node):
        if self.__check_tokentype(token.ELIF):
            self.__advance()
            elif_stmt_node = ast.BasicIf()
            elif_stmt_node.bool_expr = self.__bexpr()
            self.__eat(token.THEN)
            elif_stmt_node.stmt_list = self.__bstmts(ast.StmtList())
            if_stmt_node.elseifs.append(elif_stmt_node)
            return self.__condt(if_stmt_node)
        elif self.__check_tokentype(token.ELSE):
            self.__advance()
            if_stmt_node.has_else = True
            if_stmt_node.else_stmts = self.__bstmts(ast.StmtList())
        return if_stmt_node
        
    def __while(self):
        self.__eat(token.WHILE)
        while_stmt_node = ast.WhileStmt()
        while_stmt_node.bool_expr = self.__bexpr()
        self.__eat(token.DO)
        while_stmt_node.stmt_list = self.__bstmts(ast.StmtList())
        self.__eat(token.END)
        return while_stmt_node

    def __expr(self):
        expr_node = None
        if self.__check_tokentype(token.LPAREN):
            self.__advance()
            expr_node = self.__expr()
            self.__eat(token.RPAREN)
        else:
            expr_node = self.__rvalue()
        mathrels = [token.PLUS, token.MINUS, token.DIVIDE, token.MULTIPLY, token.MODULO]
        if self.current_token.tokentype in mathrels:
            complex_expr_node = ast.ComplexExpr()
            complex_expr_node.first_operand = expr_node
            complex_expr_node.math_rel = self.current_token
            self.__advance()
            complex_expr_node.rest = self.__expr()
            return complex_expr_node
        else:
            simple_expr_node = ast.SimpleExpr()
            simple_expr_node.term = expr_node
            return simple_expr_node

    def __rvalue(self):
        rvals = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL]
        # note that this list does not contain token.NEW or token.ID bc of sequence new id
        curr_token = self.current_token
        if curr_token.tokentype in rvals:
            simple_rvalue_node = ast.SimpleRValue()
            simple_rvalue_node.val = self.current_token
            self.__eat(curr_token.tokentype)
            return simple_rvalue_node
        elif curr_token.tokentype == token.NEW:
            self.__advance()
            new_rvalue_node = ast.NewRValue()
            new_rvalue_node.struct_type = self.current_token 
            self.__eat(token.ID)
            return new_rvalue_node
        else:
            return self.__idrval()

    def __idrval(self):
        id_token = self.current_token
        self.__eat(token.ID)
        if self.__check_tokentype(token.LPAREN):
            self.__advance()
            call_rval = ast.CallRValue()
            call_rval.fun = id_token
            call_rval.args = self.__exprlist()
            self.__eat(token.RPAREN)
            return call_rval
        else:
            id_rval = ast.IDRvalue()
            id_rval.path.append(id_token)
            while self.__check_tokentype(token.DOT):
                self.__advance()
                id_rval.path.append(self.current_token)
                self.__eat(token.ID)
            return id_rval

    def __exprlist(self):
        exprs = []
        types = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL, token.NEW, token.ID, token.LPAREN]
        if self.current_token.tokentype in types:
            exprs.append(self.__expr())
            while self.current_token.tokentype == token.COMMA:
                self.__advance()
                exprs.append(self.__expr())
        return exprs

    def __bexpr(self):
        bexpr_node = ast.BoolExpr()
        if self.__check_tokentype(token.NOT):
            self.__advance()
            bexpr_node.negated = True
            bexpr_node.first_expr = self.__bexpr()
            return self.__bexprt(bexpr_node)
        elif self.__check_tokentype(token.LPAREN):
            self.__advance()
            bexpr_node.first_expr = self.__bexpr()
            self.__eat(token.RPAREN)
            return self.__bconnct(bexpr_node)
        else:
            bexpr_node.first_expr = self.__expr()
            return self.__bexprt(bexpr_node)

    def __bexprt(self, bexpr_node):
        possible_tokens = [token.EQUAL, token.LESS_THAN, token.GREATER_THAN, token.LESS_THAN_EQUAL, token.GREATER_THAN_EQUAL, token.NOT_EQUAL]
        curr_token = self.current_token
        if curr_token.tokentype in possible_tokens:
            bexpr_node.bool_rel = curr_token
            self.__advance()
            bexpr_node.second_expr = self.__expr()
        bexpr_node = self.__bconnct(bexpr_node)
        return self.__bconnct(bexpr_node)

    def __bconnct(self, bexpr_node):
        possible_tokens = [token.AND, token.OR]
        curr_token = self.current_token
        if curr_token.tokentype in possible_tokens:
            bexpr_node.bool_connector = curr_token
            self.__advance()
            bexpr_node.rest = self.__bexpr()
        return bexpr_node
