# !/usr/bin/python3
#
# Author: Kasey Davis
# Assignment: 4
# Description:
#   Simple script to executre the MyPL parser and pretty printer.
# ------------------------------------------------------------------------


import mypl_error as error
import mypl_lexer as lexer
import mypl_token as token
import mypl_ast as ast


class Parser(object):

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None

    def parse(self):
        """succeeds if program is syntactically well-formed"""
        stmt_list_node = ast.StmtList()
        self.__advance()
        self.__stmts(stmt_list_node)
        self.__eat(token.EOS, 'expecting end of file')
        return stmt_list_node

    def __advance(self):
        self.current_token = self.lexer.next_token()

    def __eat(self, tokentype, error_msg):
        if self.current_token.tokentype == tokentype:
            self.__advance()
        else:
            self.__error(error_msg)

    def __error(self, error_msg):
        s = error_msg + ', found "' + self.current_token.lexeme + '" in parser'
        l = self.current_token.line
        c = self.current_token.column
        raise error.MyPLError(s, l, c)

    def __tokenIs(self, tokenType):
        return self.current_token.tokentype == tokenType

    # Beginning of recursive descent functions

    def __stmts(self, stmt_list_node):
        """<stmts> ::= <stmt> <stmts> | e"""
        if not self.__tokenIs(token.EOS):
            self.__stmt(stmt_list_node)
            self.__stmts(stmt_list_node)

    def __stmt(self, stmt_list_node):
        """<stmt> ::= <sdecl> | <fdecl> | <bstmt>"""
        if self.__tokenIs(token.STRUCTTYPE):
            struct_decl_node = self.__sdecl()
            stmt_list_node.stmts.append(struct_decl_node)
        elif self.__tokenIs(token.FUN):
            stmt_list_node.stmts.append(self.__fdecl())
        else:
            stmt_list_node.stmts.append(self.__bstmt())

    def __bstmts(self, bstmts):
        """<bstmts> ::= <bstmt> <bstmts> | e"""
        bstmtStarts = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL,
                       token.NIL, token.LPAREN, token.VAR, token.SET, token.IF, token.WHILE, token.RETURN, token.NEW, token.ID]

        if self.current_token.tokentype in bstmtStarts:
            bstmts.append(self.__bstmt())
            self.__bstmts(bstmts)
        else:
            pass

    def __bstmt(self):
        """<bstmt> ::= <vdecl> | <assign> | <cond> | <while> | <expr> SEMICOLON | <exit>"""

        exprStarts = [token.STRINGVAL, token.INTVAL,
                      token.BOOLVAL, token.FLOATVAL, token.NIL, token.LPAREN, token.NEW, token.ID]
        bstmt = None

        if self.__tokenIs(token.VAR):
            bstmt = self.__vdecl()
        elif self.__tokenIs(token.SET):
            bstmt = self.__assign()
        elif self.__tokenIs(token.IF):
            bstmt = self.__cond()
        elif self.__tokenIs(token.WHILE):
            bstmt = self.__while()
        elif self.current_token.tokentype in exprStarts:
            bstmt = ast.ExprStmt()
            bstmt.expr = self.__expr()
            self.__eat(token.SEMICOLON, "expected ';'")
        else:
            bstmt = self.__exit()

        return bstmt

    def __sdecl(self):
        """<sdecl> ::= STRUCT ID <vdecls> END"""
        struct_decl_node = ast.StructDeclStmt()
        self.__eat(token.STRUCTTYPE, "expected 'struct'")
        struct_decl_node.struct_id = self.current_token
        self.__eat(token.ID, "expected struct ID")
        self.__vdecls(struct_decl_node)
        self.__eat(token.END, "expected 'end'")
        return struct_decl_node

    def __vdecls(self, struct_decl_node):
        """<vdecls> ::= <vdecl> <vdecls> | e"""
        if self.__tokenIs(token.VAR):
            var_decl = self.__vdecl()
            struct_decl_node.var_decls.append(var_decl)
            self.__vdecls(struct_decl_node)
        else:
            pass

    def __fdecl(self):
        """<fdecl> ::= FUN ( <type> | NIL ) ID LPAREN <params> RPAREN <bstmts> END"""
        fun_decl_stmt = ast.FunDeclStmt()

        self.__eat(token.FUN, "expected FUN token")

        fun_decl_stmt.return_type = self.current_token

        types = [token.ID, token.INTTYPE, token.FLOATTYPE,
                 token.BOOLTYPE, token.STRINGTYPE]

        if self.current_token.tokentype in types:
            self.__type()
        elif self.__tokenIs(token.NIL):
            self.__advance()
        else:
            self.__error("Expected type or nil")

        fun_decl_stmt.fun_name = self.current_token
        self.__eat(token.ID, "expected ID")
        self.__eat(token.LPAREN, "expected '('")
        fun_decl_stmt.params = self.__params()
        self.__eat(token.RPAREN, "expected ')'")

        self.__bstmts(fun_decl_stmt.stmt_list.stmts)
        self.__eat(token.END, "expected END")

        return fun_decl_stmt

    def __params(self):
        """<params> ::= ID COLON <type> ( COMMA ID COLON <type> )* | e"""
        params = []
        if self.__tokenIs(token.ID):
            params = []
            new_param = ast.FunParam()
            new_param.param_name = self.current_token
            self.__advance()
            self.__eat(token.COLON, "expected ':'")
            new_param.param_type = self.current_token
            params.append(new_param)
            self.__type()

            while(self.__tokenIs(token.COMMA)):
                new_param = ast.FunParam()
                self.__advance()
                new_param.param_name = self.current_token
                self.__eat(token.ID, "expected ID")
                self.__eat(token.COLON, "expected ':'")
                new_param.param_type = self.current_token
                params.append(new_param)
                self.__type()

        else:
            pass

        return params

    def __type(self):
        """<type> ::= ID | INTTYPE | FLOATTYPE | BOOLTYPE | STRINGTYPE"""

        types = [token.ID, token.INTTYPE, token.FLOATTYPE,
                 token.BOOLTYPE, token.STRINGTYPE]

        if self.current_token.tokentype in types:
            self.__advance()

        else:
            self.__error("Expected type, recieved none or invalid")

    def __exit(self):
        """<exit> ::= RETURN ( <expr> | e ) SEMICOLON"""
        exprStarts = [token.STRINGVAL, token.INTVAL,
                      token.BOOLVAL, token.FLOATVAL, token.NIL, token.LPAREN, token.ID]

        return_stmt = ast.ReturnStmt()
        return_stmt.return_token = self.current_token
        self.__eat(token.RETURN, "expected 'return'")

        if self.current_token.tokentype in exprStarts:
            return_stmt.return_expr = self.__expr()
        else:
            pass

        self.__eat(token.SEMICOLON, "expected ';'")

        return return_stmt

    def __vdecl(self):
        """<vdecl> ::= VAR ID <tdecl> ASSIGN <expr> SEMICOLON"""
        var_decl = ast.VarDeclStmt()
        self.__eat(token.VAR, "expected 'var'")
        var_decl.var_id = self.current_token
        self.__eat(token.ID, "expected var ID")
        self.__tdecl(var_decl)
        self.__eat(token.ASSIGN, "expected '='")
        var_decl.var_expr = self.__expr()
        self.__eat(token.SEMICOLON, "expected ';'")
        return var_decl

    def __tdecl(self, var_decl):
        """<tdecl> ::= COLON <type> | e"""
        if self.__tokenIs(token.COLON):
            self.__advance()
            var_decl.var_type = self.current_token
            self.__type()
        else:
            pass

    def __assign(self):
        """<assign> ::= SET <lvalue> ASSIGN <expr> SEMICOLON"""
        assign_stmt = ast.AssignStmt()
        self.__eat(token.SET, "expected 'SET'")
        assign_stmt.lhs = self.__lvalue()
        self.__eat(token.ASSIGN, "expected '='")
        assign_stmt.rhs = self.__expr()
        self.__eat(token.SEMICOLON, "expected ';'")
        return assign_stmt

    def __lvalue(self):
        """<lvalue> ::= ID ( DOT ID )*"""
        lvalue = ast.LValue()
        lvalue.path.append(self.current_token)
        self.__eat(token.ID, "expected ID")

        while self.__tokenIs(token.DOT):
            self.__advance()
            lvalue.path.append(self.current_token)
            self.__eat(token.ID, "expected 'ID'")
        return lvalue

    def __cond(self):
        """<cond> ::= IF <bexpr> THEN <bstmts> <condt> END"""
        if_stmt = ast.IfStmt()
        if_stmt.if_part = ast.BasicIf()

        self.__eat(token.IF, "expected 'if'")
        if_stmt.if_part.bool_expr = self.__bexpr()
        self.__eat(token.THEN, "expected 'then'")
        if_stmt.if_part.stmt_list = ast.StmtList()
        self.__bstmts(if_stmt.if_part.stmt_list.stmts)
        if_stmt.has_else = False
        self.__condt(if_stmt)
        self.__eat(token.END, "expected 'end'")

        return if_stmt

    def __condt(self, if_stmt):
        """<condt> ::= ELIF <bexpr> THEN <bstmts> <condt> | ELSE <bstmts> | e"""

        if self.__tokenIs(token.ELIF):
            basic_else_if = ast.BasicIf()
            self.__advance()
            basic_else_if.bool_expr = self.__bexpr()
            self.__eat(token.THEN, "expected 'then'")
            self.__bstmts(basic_else_if.stmt_list.stmts)
            if_stmt.elseifs.append(basic_else_if)
            self.__condt(if_stmt)
        elif self.__tokenIs(token.ELSE):
            if_stmt.has_else = True
            self.__advance()
            self.__bstmts(if_stmt.else_stmts.stmts)
        else:
            pass

    def __while(self):
        """<while> ::= WHILE <bexpr> DO <bstmts> END"""
        while_stmt = ast.WhileStmt()
        self.__eat(token.WHILE, "expected 'while'")
        while_stmt.bool_expr = self.__bexpr()
        self.__eat(token.DO, "expected 'do'")
        self.__bstmts(while_stmt.stmt_list.stmts)
        self.__eat(token.END, "expected end")

        return while_stmt

    def __expr(self):
        """<expr> ::= ( <rvalue> | LPAREN <expr> RPAREN ) ( <mathrel> <expr> | e )"""
        rvalues = [token.STRINGVAL, token.INTVAL,
                   token.BOOLVAL, token.FLOATVAL, token.NIL, token.NEW, token.ID]
        expr = None
        rvalue = None
        if self.current_token.tokentype in rvalues:
            rvalue = self.__rvalue()
        elif self.__tokenIs(token.LPAREN):
            self.__eat(token.LPAREN, "expected '('")
            rvalue = self.__expr()
            self.__eat(token.RPAREN, "expected ')'")
        else:
            self.__error(
                "expected right-hand-side assignment value or expression")

        mathrels = [token.PLUS, token.MINUS,
                    token.DIVIDE, token.MULTIPLY, token.MODULO]
        if self.current_token.tokentype in mathrels:
            expr = ast.ComplexExpr()
            expr.first_operand = rvalue
            expr.math_rel = self.current_token
            self.__mathrel()
            expr.rest = self.__expr()
        else:
            expr = ast.SimpleExpr()
            expr.term = rvalue
        return expr

    def __mathrel(self):
        """<mathrel> ::= PLUS | MINUS | DIVIDE | MULTIPLY | MODULO """
        # The operators are checked at the only location where self.__mathrel() is called
        self.__advance()

    def __rvalue(self):
        """<rvalue> ::= STRINGVAL | INTVAL | BOOLVAL | FLOATVAL | NIL | NEW ID | <idrval> """
        rvalues = [token.STRINGVAL, token.INTVAL,
                   token.BOOLVAL, token.FLOATVAL, token.NIL]

        rval = None
        if self.current_token.tokentype in rvalues:
            rval = ast.SimpleRValue()
            rval.val = self.current_token
            self.__advance()
        elif self.__tokenIs(token.NEW):
            self.__advance()
            rval = ast.NewRValue()
            rval.struct_type = self.current_token
            self.__eat(token.ID, "expected an ID")
        else:
            rval = self.__idrval()
        return rval

    def __idrval(self):
        """<idrvalue> ::= ID ( DOT ID )* | ID LPAREN <exprlist> RPAREN """

        idrval = ast.IDRvalue()
        idrval.path.append(self.current_token)
        call_rval = ast.CallRValue()
        call_rval.fun = self.current_token

        self.__eat(token.ID, "expected an ID")

        is_id_not_call = None
        if self.__tokenIs(token.LPAREN):
            is_id_not_call = False
            self.__advance()
            self.__exprlist(call_rval.args)
            self.__eat(token.RPAREN, "expected ')'")

        else:
            is_id_not_call = True

            while self.__tokenIs(token.DOT):
                self.__advance()
                idrval.path.append(self.current_token)

                self.__eat(token.ID, "expected an ID")

        if(is_id_not_call):
            return idrval
        else:
            return call_rval

    def __exprlist(self, exprlist):
        """<exprlist> ::= <expr> ( COMMA <expr> )* | e """
        exprStarts = [token.STRINGVAL, token.INTVAL,
                      token.BOOLVAL, token.FLOATVAL, token.NIL, token.NEW, token.ID, token.LPAREN]
        if self.current_token.tokentype in exprStarts:
            exprlist.append(self.__expr())

            while self.__tokenIs(token.COMMA):
                self.__advance()
                exprlist.append(self.__expr())
        else:
            pass

    def __bexpr(self):
        """<bexpr> ::= <expr> <bexprt> | NOT <bexpr> <bexprt> | LPAREN <bexpr> RPAREN <bconnct> """
        bexpr = ast.BoolExpr()
        if self.__tokenIs(token.NOT):
            bexpr.negated = True
            self.__advance()
            bexpr.first_expr = self.__bexpr()
            self.__bexprt(bexpr)
        elif self.__tokenIs(token.LPAREN):
            bexpr.negated = False
            self.__advance()
            bexpr.first_expr = self.__bexpr()
            self.__eat(token.RPAREN, "expected ')'")
            self.__bconnct(bexpr)
        else:
            bexpr.negated = False
            bexpr.first_expr = self.__expr()
            self.__bexprt(bexpr)

        return bexpr

    def __bexprt(self, bexpr):
        """<bexprt> ::= <boolrel> <expr> <bconnct> | <bconnct> """
        boolrelStarts = [token.EQUAL, token.LESS_THAN, token.GREATER_THAN,
                         token.LESS_THAN_EQUAL, token.GREATER_THAN_EQUAL, token.NOT_EQUAL]
        if self.current_token.tokentype in boolrelStarts:
            bexpr.bool_rel = self.current_token
            self.__boolrel()
            bexpr.second_expr = self.__expr()
            self.__bconnct(bexpr)
        else:
            self.__bconnct(bexpr)

    def __bconnct(self, bexpr):
        """<bconnct> ::= AND <bexpr> | OR <bexpr> | e """
        if self.__tokenIs(token.AND):
            bexpr.bool_connector = self.current_token
            self.__advance()
            bexpr.rest = self.__bexpr()
        elif self.__tokenIs(token.OR):
            bexpr.bool_connector = self.current_token
            self.__advance()
            bexpr.rest = self.__bexpr()
        else:
            pass

    def __boolrel(self):
        """<boolrel> ::= EQUAL | LESS_THAN | GREATER_THAN | LESS_THAN_EQUAL | GREATER_THAN_EQUAL | NOT_EQUAL """
        # Relational operators are checked in __bexprt()
        self.__advance()
