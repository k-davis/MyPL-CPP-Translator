import mypl_token as token
import mypl_ast as ast


class NameMangler(ast.Visitor):

    def mangle_token(self, token):
        token.lexeme = "mypl_" + token.lexeme

    def visit_stmt_list(self, stmt_list):
        for stmt in stmt_list.stmts:
            stmt.accept(self)

    def visit_expr_stmt(self, expr_stmt):
        expr_stmt.expr.accept(self)

    def visit_var_decl_stmt(self, var_decl):
        var_decl.var_expr.accept(self)
        self.mangle_token(var_decl.var_id)

    def visit_assign_stmt(self, assign_stmt):

        assign_stmt.rhs.accept(self)
        assign_stmt.lhs.accept(self)

    def visit_simple_expr(self, simple_expr):
        simple_expr.term.accept(self)

    def visit_simple_rvalue(self, r_val):
        pass

    def visit_new_rvalue(self, r_val):
        self.mangle_token(r_val.struct_type)

    def visit_call_rvalue(self, r_val):
        self.mangle_token(r_val.fun)
        for arg in r_val.args:
            arg.accept(self)

    def visit_id_rvalue(self, r_val):
        for tkn in r_val.path:
            self.mangle_token(tkn)

    def visit_complex_expr(self, expr):
        expr.first_operand.accept(self)
        expr.rest.accept(self)

    def visit_bool_expr(self, b_expr):
        b_expr.first_expr.accept(self)

        if b_expr.bool_rel:
            b_expr.second_expr.accept(self)

        if b_expr.bool_connector:
            b_expr.rest.accept(self)

    def visit_lvalue(self, lval):
        for tkn in lval.path:
            self.mangle_token(tkn)

    def visit_if_stmt(self, if_stmt):
        if_stmt.if_part.bool_expr.accept(self)

        if_stmt.if_part.stmt_list.accept(self)

        for elem in if_stmt.elseifs:
            elem.bool_expr.accept(self)

            elem.stmt_list.accept(self)

        if if_stmt.has_else:
            if_stmt.else_stmts.accept(self)

    def visit_while_stmt(self, while_stmt):
        while_stmt.bool_expr.accept(self)

        while_stmt.stmt_list.accept(self)

    def visit_struct_decl_stmt(self, struct_decl):
        self.mangle_token(struct_decl.struct_id)

        for v_decl in struct_decl.var_decls:
            v_decl.accept(self)

    def visit_fun_decl_stmt(self, fun_decl):
        self.mangle_token(fun_decl.fun_name)
        for param in fun_decl.params:
            self.mangle_token(param.param_name)

        fun_decl.stmt_list.accept(self)

    def visit_return_stmt(self, return_stmt):
        if return_stmt.return_expr:
            return_stmt.return_expr.accept(self)
