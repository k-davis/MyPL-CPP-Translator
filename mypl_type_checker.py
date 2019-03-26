#!/usr/bin/python3
#
# Author: Kasey Davis
# Assignment: 5
# Description:
#   Simple script to execute the MyPL type checker.
# ---------------------------------------------------------------

import mypl_token as token
import mypl_ast as ast
import mypl_error as error
import mypl_symbol_table as symbol_table


class TypeChecker(ast.Visitor):
    """A MyPL type checker visitor implementation where struct types
    take the form: type_id -> {v1:t1, ..., vn:tn} and function types
    take the form: fun_id -> [[t1, t2, .., tn], return_type]
    """

    def __init__(self):
        # initialize the sumbol table (for ids -> types)
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
        # ... put remaining built-in function types here ...

        self.sym_table.add_id('length')
        self.sym_table.set_info('length', [[token.STRINGTYPE], token.INTTYPE])

        self.sym_table.add_id('get')
        self.sym_table.set_info(
            'get', [[token.INTTYPE, token.STRINGTYPE], token.STRINGTYPE])

        self.sym_table.add_id('reads')
        self.sym_table.set_info('reads', [[], token.STRINGTYPE])

        self.sym_table.add_id('readi')
        self.sym_table.set_info('readi', [[], token.INTTYPE])

        self.sym_table.add_id('readf')
        self.sym_table.set_info('readf', [[], token.FLOATTYPE])

        self.sym_table.add_id('itos')
        self.sym_table.set_info('itos', [[token.INTTYPE], token.STRINGTYPE])

        self.sym_table.add_id('itof')
        self.sym_table.set_info('itof', [[token.INTTYPE], token.FLOATTYPE])

        self.sym_table.add_id('ftos')
        self.sym_table.set_info('ftos', [[token.FLOATTYPE], token.STRINGTYPE])

        self.sym_table.add_id('stoi')
        self.sym_table.set_info('stoi', [[token.STRINGTYPE], token.INTTYPE])

        self.sym_table.add_id('stof')
        self.sym_table.set_info('stof', [[token.STRINGTYPE], token.FLOATTYPE])

        self.sym_table.add_id('btos')
        self.sym_table.set_info('btos', [[token.BOOLTYPE], token.STRINGTYPE])

        self.primitive_types = [
            token.INTTYPE, token.FLOATTYPE, token.BOOLTYPE, token.STRINGTYPE]

    # Converts value tokens to their type, including for structs
    def __type_from_token(self, tkn):
        translation_dict = {token.INTVAL: token.INTTYPE,
                            token.FLOATVAL: token.FLOATTYPE,
                            token.STRINGVAL: token.STRINGTYPE,
                            token.BOOLVAL: token.BOOLTYPE,
                            token.ID: tkn.lexeme}

        if tkn.tokentype in translation_dict:
            return translation_dict[tkn.tokentype]
        else:
            return tkn.tokentype

    # checks if the arguments of a function match its parameters
    def __do_args_match_params(self, args, params):
        if len(args) != len(params):
            return False

        for idx, param in enumerate(params):
            if param not in [args[idx], token.NIL]:
                return False

        return True

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
        self.sym_table.add_id(var_decl.var_id.lexeme)

        var_decl.var_expr.accept(self)
        rhs_expr_type = self.current_type

        if var_decl.var_type:
            are_either_nil = token.NIL in [
                self.__type_from_token(var_decl.var_type), rhs_expr_type]

            if self.__type_from_token(var_decl.var_type) != rhs_expr_type and not are_either_nil:
                msg = 'Mismatching types'
                self.__error(msg, var_decl.var_id)

            if var_decl.var_type.tokentype != token.NIL or rhs_expr_type == token.NIL:
                # rule 8 and 9
                var_type = self.__type_from_token(var_decl.var_type)
            else:
                msg = 'Invalid typing at variable declaration'
                self.__error(msg, var_decl.var_id)
        elif rhs_expr_type != token.NIL:
            var_type = rhs_expr_type
        else:
            msg = "Invalid typing at variable declaration"
            self.__error(msg, var_decl.var_id)

        self.current_type = var_type
        self.sym_table.set_info(var_decl.var_id.lexeme, var_type)

    def visit_assign_stmt(self, assign_stmt):
        assign_stmt.rhs.accept(self)
        rhs_type = self.current_type
        assign_stmt.lhs.accept(self)
        lhs_type = self.current_type

        if rhs_type != token.NIL and rhs_type != lhs_type:
            msg = 'mismatch type in assignment'
            self.__error(msg, assign_stmt.lhs.path[0])

    def visit_simple_expr(self, simple_expr):
        simple_expr.term.accept(self)

    def visit_simple_rvalue(self, r_val):
        self.current_type = self.__type_from_token(r_val.val)

    def visit_new_rvalue(self, r_val):
        self.current_type = r_val.struct_type.lexeme

    def visit_call_rvalue(self, r_val):
        id_lexeme = r_val.fun.lexeme
        if self.sym_table.id_exists(id_lexeme):
            table_args = self.sym_table.get_info(id_lexeme)

            r_args = []
            for expr in r_val.args:
                expr.accept(self)
                r_args.append(self.current_type)

            if not self.__do_args_match_params(table_args[0], r_args):
                msg = 'mismatch in function signatures'
                self.__error(msg, r_val.fun)

            self.current_type = table_args[1]

        else:
            msg = 'function "' + id_lexeme + '" is unknown here'
            self.__error(msg, r_val.fun)

    def visit_id_rvalue(self, r_val):
        idx = 0

        if not self.sym_table.id_exists(self.__type_from_token(r_val.path[0])):
            msg = 'Variable does not exist'
            self.__error(msg, r_val.path[0])

        struct_t = self.sym_table.get_info(r_val.path[0].lexeme)
        final_type = struct_t
        while idx + 1 < len(r_val.path):
            struct_info = self.sym_table.get_info(struct_t)
            var_id = r_val.path[idx + 1].lexeme
            if var_id in struct_info:
                var_type = struct_info[var_id]
            else:
                msg = 'Variable not member variable of struct'
                self.__error(msg, r_val.path[idx + 1])

            if idx + 2 < len(r_val.path):
                struct_t = var_type
            else:
                final_type = var_type

            idx += 1
        self.current_type = final_type

        if idx < len(r_val.path) - 1:
            msg = "Variable does not have member variable"
            self.__error(msg, r_val.path[idx + 1])

    def visit_complex_expr(self, expr):
        expr.first_operand.accept(self)
        f_op = self.current_type
        expr.rest.accept(self)
        s_op = self.current_type

        if f_op != s_op:
            msg = "mismatching operands surrounding operator"
            self.__error(msg, expr.math_rel)

        if expr.math_rel.tokentype == token.PLUS:
            if f_op not in [token.STRINGTYPE, token.INTTYPE, token.FLOATTYPE]:
                msg = "Invalid operand types for plus operator"
                self.__error(msg, expr.math_rel)
        elif expr.math_rel.tokentype in [token.MINUS, token.MULTIPLY, token.DIVIDE]:
            if f_op not in [token.INTTYPE, token.FLOATTYPE]:
                msg = "Invalid operand types for operator"
                self.__error(msg, expr.math_rel)
        else:       # token is modulo
            if f_op not in [token.INTTYPE]:
                msg = "invalid operand types for modulo operator"
                self.__error(msg, expr.math_rel)

        self.current_type = f_op

    def visit_bool_expr(self, b_expr):
        b_expr.first_expr.accept(self)
        f_expr_t = self.current_type

        if b_expr.second_expr:
            b_expr.second_expr.accept(self)
            s_expr_t = self.current_type

            if b_expr.bool_rel.tokentype in [token.EQUAL, token.NOT_EQUAL]:
                if f_expr_t == s_expr_t:
                    # rule 19
                    if f_expr_t in [token.INTTYPE, token.FLOATTYPE, token.BOOLTYPE, token.STRINGTYPE, token.NIL, f_expr_t if self.sym_table.id_exists(f_expr_t) else None]:
                        pass
                    else:
                        msg = 'Invalid type in boolean relation'
                        self.__error(msg, b_expr.bool_rel)
                elif f_expr_t == token.NIL or s_expr_t == token.NIL:
                    expr_t = None
                    if f_expr_t == token.NIL:
                        expr_t = s_expr_t
                    else:
                        expr_t = f_expr_t

                    if expr_t in [token.INTTYPE, token.FLOATTYPE, token.BOOLTYPE, token.STRINGTYPE, expr_t if self.sym_table.id_exists(f_expr_t) else None]:
                        pass
                    else:
                        msg = 'Invalid type in boolean equality relation'
                        self.__error(msg, b_expr.bool_rel)
                else:
                    msg = 'Inavlid types in boolean relation'
                    self.__error(msg, b_expr.bool_rel)

            elif b_expr.bool_rel.tokentype in [token.LESS_THAN, token.GREATER_THAN, token.LESS_THAN_EQUAL, token.GREATER_THAN_EQUAL]:
                if f_expr_t == s_expr_t:
                    if f_expr_t in [token.INTTYPE, token.FLOATTYPE, token.BOOLTYPE, token.STRINGTYPE]:
                        pass
                    else:
                        msg = 'Invalid types, they are uncomparable'
                        self.__error(msg, b_expr.bool_rel)
                else:
                    msg = "Types must be identical for comparison operator"
                    self.__error(msg, b_expr.bool_rel)
                pass
            else:
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

            if b_expr.rest:
                b_expr.rest.accept(self)
                rest_t = self.current_type

        self.current_type = token.BOOLTYPE

        # ... finish remaining visit calls ...

    def visit_lvalue(self, lval):
        idx = 0

        if not self.sym_table.id_exists(self.__type_from_token(lval.path[0])):
            msg = 'Variable does not exist'
            self.__error(msg, lval.path[0])

        struct_t = self.sym_table.get_info(lval.path[0].lexeme)
        final_type = struct_t
        while idx + 1 < len(lval.path):
            struct_info = self.sym_table.get_info(struct_t)
            var_id = lval.path[idx + 1].lexeme
            if var_id in struct_info:
                var_type = struct_info[var_id]
            else:
                msg = 'Variable not member variable of struct'
                self.__error(msg, lval.path[idx + 1])

            if idx + 2 < len(lval.path):
                struct_t = var_type
            else:
                final_type = var_type

            idx += 1
        self.current_type = final_type

    def visit_if_stmt(self, if_stmt):
        self.sym_table.push_environment()

        if_stmt.if_part.bool_expr.accept(self)
        if_t = self.current_type

        if if_t != token.BOOLTYPE:
            msg = 'Conditional expression not of boolean type'
            self.__error(msg, None)

        if_stmt.if_part.stmt_list.accept(self)

        for elem in if_stmt.elseifs:
            elem.bool_expr.accept(self)
            if self.current_type != token.BOOLTYPE:
                msg = 'Conditional expression not of boolean type'
                self.__error(msg, None)

            elem.stmt_list.accept(self)

        if if_stmt.has_else:
            if_stmt.else_stmts.accept(self)

        self.sym_table.pop_environment()

    def visit_while_stmt(self, while_stmt):
        self.sym_table.push_environment()
        while_stmt.bool_expr.accept(self)
        be_t = self.current_type

        if be_t != token.BOOLTYPE:
            msg = 'Conditional expression not of boolean type'
            self.__error(msg, None)

        while_stmt.stmt_list.accept(self)

        self.sym_table.pop_environment()

    def visit_struct_decl_stmt(self, struct_decl):
        self.sym_table.push_environment()
        types = {}

        for v_decl in struct_decl.var_decls:
            v_decl.accept(self)
            v_t = self.current_type
            types[v_decl.var_id.lexeme] = v_t
        self.sym_table.pop_environment()

        self.sym_table.add_id(struct_decl.struct_id.lexeme)
        self.sym_table.set_info(struct_decl.struct_id.lexeme, types)

    def visit_fun_decl_stmt(self, fun_decl):

        self.sym_table.add_id(fun_decl.fun_name.lexeme)
        return_t = self.__type_from_token(fun_decl.return_type)
        param_ts = []

        for param in fun_decl.params:
            param_ts.append(self.__type_from_token(param.param_type))

        for i in range(len(fun_decl.params)):
            for j in range(i + 1, len(fun_decl.params)):
                if fun_decl.params[i].param_name.lexeme == fun_decl.params[j].param_name.lexeme:
                    msg = "Duplicate parameters in function defintion"
                    self.__error(msg, fun_decl.params[j].param_name)

        self.sym_table.set_info(fun_decl.fun_name.lexeme, [param_ts, return_t])

        self.sym_table.push_environment()
        for param in fun_decl.params:
            self.sym_table.add_id(param.param_name.lexeme)
            self.sym_table.set_info(
                param.param_name.lexeme, self.__type_from_token(param.param_type))

        fun_decl.stmt_list.accept(self)
        self.sym_table.pop_environment()

    def visit_return_stmt(self, return_stmt):
        if return_stmt.return_expr:
            return_stmt.return_expr.accept(self)
            return_t = self.current_type
            if self.sym_table.get_scope_level() == 1:
                if return_t not in [token.NIL, token.INTTYPE]:
                    msg = 'Return in outermost scope must return int or nil'
                    self.__error(msg, return_stmt.return_token)
