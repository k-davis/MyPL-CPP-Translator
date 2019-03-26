import mypl_token as token
import mypl_ast as ast
import mypl_error as error
import mypl_symbol_table as sym_tbl

class ReturnException(Exception): pass

class Interpreter(ast.Visitor):
    """A MyPL interpret visitor implementation"""

    def run(self, stmt_list):
        try:
            stmt_list.accept(self)
        except ReturnException:
            pass

    def __init__(self):
        # initialize the symbol table (for ids -> values)
        self.sym_table = sym_tbl.SymbolTable()
        # holds the type of expression type
        self.current_value = None
        # the heap {oid:struct_id}
        self.heap = {}

    def __error(self, msg, the_token):
        raise error.MyPLError(msg, the_token.line. the_token.column)

    def __built_in_fun_helper(self, call_rvalue):
        func = call_rvalue.fun.lexeme
        arg_vals = []

        for expr in call_rvalue.args:
            expr.accept(self)
            arg_vals.append(self.current_value)

        for i, arg in enumerate(arg_vals):
            if arg is None:
                msg = 'Argument is nil at invalid location'
                self.__error(msg, call_rvalue.fun)

        if func == 'print':
            arg_vals[0] = arg_vals[0].replace(r'\n', '\n')
            print(arg_vals[0], end='')
        elif func == 'length':
            self.current_value = len(arg_vals[0])
        elif func == 'get':
            if 0 <= arg_vals[0] < len(arg_vals[1]):
                self.current_value = arg_vals[1][arg_vals[0]]
            else:
                msg = 'Array Out of Bounds error'
                self.__error(msg, call_rvalue.fun)
        elif func == 'reads':
            self.current_value = input()
        elif func == 'readi':
            try:
                self.current_value = int(input())
            except ValueError:
                self.__error('bad int value',  call_rvalue.fun)
        elif func == 'readf':
            try:
                self.current_value = float(input())
            except ValueError:
                self.__error('bad float value',  call_rvalue.fun)
        elif func == 'itos':
            self.current_value = str(arg_vals[0])
        elif func == 'itof':
            self.current_value = float(arg_vals[0])
        elif func == 'ftos':
            self.current_value = str(arg_vals[0])
        elif func == 'stoi':
            try:
                self.current_value = int(arg_vals[0])
            except ValueError:
                self.__error('bad string value', call_rvalue.fun)
        elif func == 'stof':
            try:
                self.current_value = float(arg_vals[0])
            except ValueError:
                self.__error('bad string value', call_rvalue.fun)
        elif func == 'btos':
            self.current_value = str(arg_vals[0])

    def visit_stmt_list(self, stmt_list):
        self.sym_table.push_environment()
        for stmt in stmt_list.stmts:
            stmt.accept(self)
        self.sym_table.pop_environment()

    def visit_expr_stmt(self, expr_stmt):
        expr_stmt.expr.accept(self)

    def visit_var_decl_stmt(self, var_decl):
        var_decl.var_expr.accept(self)
        exp_value = self.current_value
        var_name = var_decl.var_id.lexeme
        cur_env = self.sym_table.get_env_id()
        
        if self.sym_table.id_exists_in_env(var_name, cur_env):
            msg = 'variable already defined in current environment'
            self.__error(msg, var_decl.var_id)
        
        self.sym_table.add_id(var_decl.var_id.lexeme)
        self.sym_table.set_info(var_decl.var_id.lexeme, exp_value)

    def visit_assign_stmt(self, assign_stmt):
        assign_stmt.rhs.accept(self)
        assign_stmt.lhs.accept(self)

    def visit_struct_decl_stmt(self, struct_decl):
        s_id = struct_decl.struct_id.lexeme
        self.sym_table.add_id(s_id)
        self.sym_table.set_info(s_id, [self.sym_table.get_env_id(), struct_decl])

    def visit_fun_decl_stmt(self, fun_decl): 
        self.sym_table.add_id(fun_decl.fun_name.lexeme)
        env_id = self.sym_table.get_env_id()
        self.sym_table.set_info(fun_decl.fun_name.lexeme, [env_id, fun_decl])

    def visit_return_stmt(self, return_stmt): 
        return_stmt.return_expr.accept(self)
        raise ReturnException()

    def visit_while_stmt(self, while_stmt):

        while_stmt.bool_expr.accept(self)
        cond = self.current_value

        while(cond):
            while_stmt.stmt_list.accept(self)
            while_stmt.bool_expr.accept(self)
            cond = self.current_value

    def visit_if_stmt(self, if_stmt):
        if_stmt.if_part.bool_expr.accept(self)
        cond = self.current_value
        if cond:
            if_stmt.if_part.stmt_list.accept(self)
        elif if_stmt.elseifs:
            for elif_b in if_stmt.elseifs:
                if not cond:
                    elif_b.bool_expr.accept(self)
                    cond = self.current_value
                    if cond:
                        elif_b.stmt_list.accept(self)
        if if_stmt.has_else and not cond:
            if_stmt.else_stmts.accept(self)

    def visit_simple_expr(self, simple_expr):
        simple_expr.term.accept(self)

    def visit_complex_expr(self, complex_expr):
        complex_expr.first_operand.accept(self)
        first_val = self.current_value

        complex_expr.rest.accept(self)
        rest_val = self.current_value

        op = complex_expr.math_rel.tokentype

        val = None
        if op == token.PLUS:
            val = first_val + rest_val
        elif op == token.MINUS:
            val = first_val - rest_val
        elif op == token.MULTIPLY:
            val = first_val * rest_val
        elif op == token.DIVIDE:
            val = first_val // rest_val
        elif op == token.MODULO:
            val = first_val % rest_val
        
        self.current_value = val

    def visit_bool_expr(self, bool_expr):
        bool_expr.first_expr.accept(self)
        f_expr_val = self.current_value

        if bool_expr.bool_rel:
            op = bool_expr.bool_rel.tokentype
            bool_expr.second_expr.accept(self)
            s_expr_val = self.current_value
            rel_result = None

            if op == token.EQUAL:
                rel_result = f_expr_val == s_expr_val
            elif op == token.NOT_EQUAL:
                rel_result = f_expr_val != s_expr_val
            elif op == token.LESS_THAN:
                rel_result = f_expr_val < s_expr_val
            elif op == token.LESS_THAN_EQUAL:
                rel_result = f_expr_val <= s_expr_val
            elif op == token.GREATER_THAN:
                rel_result = f_expr_val > s_expr_val
            elif op == token.GREATER_THAN_EQUAL:
                rel_result = f_expr_val >= s_expr_val
            

            self.current_value = rel_result
            f_expr_val = rel_result

        if bool_expr.bool_connector:
            con = bool_expr.bool_connector.tokentype
            bool_expr.rest.accept(self)
            rest_val = self.current_value
            logic_result = None

            if con == token.AND:
                logic_result = f_expr_val and rest_val
            elif con == token.OR:
                logic_result = f_expr_val or rest_val

            self.current_value = logic_result

        if bool_expr.negated:
            self.current_value = not self.current_value

    def visit_lvalue(self, lval):
        identifier = lval.path[0].lexeme
        if len(lval.path) == 1:
            self.sym_table.set_info(identifier, self.current_value)
        else:
            var_name = lval.path[0].lexeme
            var_val = self.sym_table.get_info(var_name)
            for path_id in lval.path[1:]:
                oid = var_val
                var_val = self.heap[oid][path_id.lexeme]
            self.heap[oid][path_id.lexeme] = self.current_value

    def visit_fun_param(self, fun_param): pass

    def visit_simple_rvalue(self, simple_rvalue):
        if simple_rvalue.val.tokentype == token.INTVAL:
            self.current_value = int(simple_rvalue.val.lexeme)
        elif simple_rvalue.val.tokentype == token.FLOATVAL:
            self.current_value = float(simple_rvalue.val.lexeme)
        elif simple_rvalue.val.tokentype == token.BOOLVAL:
            self.current_value = True
            if simple_rvalue.val.lexeme == 'false':
                self.current_value = False
        elif simple_rvalue.val.tokentype == token.STRINGVAL:
            self.current_value = simple_rvalue.val.lexeme
        elif simple_rvalue.val.tokentype == token.NIL:
            self.current_value = None

    def visit_new_rvalue(self, new_rvalue): 
        struct_info = self.sym_table.get_info(new_rvalue.struct_type.lexeme)
        
        cur_env = self.sym_table.get_env_id()
        self.sym_table.set_env_id(struct_info[0])

        struct_obj = {}
        self.sym_table.push_environment()
        var_decls = struct_info[1].var_decls 
        for var_decl in var_decls:
            var_decl.var_expr.accept(self)
            struct_obj[var_decl.var_id.lexeme] = self.current_value
        self.sym_table.pop_environment()
        self.sym_table.set_env_id(cur_env)

        oid = id(struct_obj)
        self.heap[oid] = struct_obj
       
        self.current_value = oid

    def visit_call_rvalue(self, call_rvalue):
        built_ins = ['print', 'length', 'get', 'readi', 'reads',
                     'readf', 'itof', 'itos', 'ftos', 'stoi', 'stof', 'btos']

        if call_rvalue.fun.lexeme in built_ins:
            self.__built_in_fun_helper(call_rvalue)
        else:
            # 1
            fun_info = self.sym_table.get_info(call_rvalue.fun.lexeme)

            # 2
            cur_env = self.sym_table.get_env_id()

            # 3
            computed_args = []
            for arg_expr in call_rvalue.args:
                arg_expr.accept(self)
                computed_args.append(self.current_value)

            # 4
            self.sym_table.set_env_id(fun_info[0])

            # 5
            self.sym_table.push_environment()

            # 6
            for idx, fun_param in enumerate(fun_info[1].params):
                id = fun_param.param_name.lexeme
                info = computed_args[idx]
                self.sym_table.add_id(id)
                self.sym_table.set_info(id, info)
            
            # 7
            try:
                for stmt in fun_info[1].stmt_list.stmts:
                    stmt.accept(self)
            except ReturnException:
                pass

            # 8 
            self.sym_table.pop_environment()

            # 9
            self.sym_table.set_env_id(cur_env)


            

    def visit_id_rvalue(self, id_rvalue):
        var_name = id_rvalue.path[0].lexeme
        var_val = self.sym_table.get_info(var_name)
        for path_id in id_rvalue.path[1:]:
            oid = var_val
            var_val = self.heap[oid][path_id.lexeme]

        self.current_value = var_val
