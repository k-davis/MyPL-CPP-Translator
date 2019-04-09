# Translator for printing a MyPL AST to a syntactically correct C++ program
#class TranslationVisitor(ast.Visitor):

import mypl_token as token
import mypl_ast as ast

class TranslationVisitor():
    """A pretty printer for turning a MyPL AST to a C++ source file"""
    def __init__(self, file_stream):
        self.indent = 4 # to increase/decrease indent level
        self.output_stream = file_stream # where printing to
        self.__basics()
        
    def __indent(self):
        """Get default indent of four spaces"""
        return ' ' * self.indent
        
    def __write(self, msg):
        self.output_stream.write(msg)

    def visit_stmt_list(self, stmt_list):
        for stmt in stmt_list.stmts:
            stmt.accept(self)

    def __basics(self):
        self.__write("#include <iostream>\n")
        self.__write("#include <string>\n")
        self.__write("\n")
        self.__write("using namespace std;\n")

        self.__write("\nvoid print(string x)\n{\n")
        self.__write("cout << x << endl;\n}\n\n")

        self.__write("\nstring itos(int x)\n{\n")
        self.__write("return to_string(x);\n}\n\n")

        #TODO functions to add -> stoi, stof
        self.__write("\nint length(string x)\n{\n")
        self.__write("return x.length();\n}\n\n")
        
        self.__write("\nchar get(int x, string y)\n{\n")
        self.__write("if(x < 0 || x > y.length()){\n")
        self.__write('return "";\n')
        self.__write("} else {\n return y.at(x);\n}\n}\n\n")
        
        self.__write("\nstring reads()\n{\n")
        self.__write("string x;\ncin >> x;\nreturn x;\n}\n\n")
        
        self.__write("\nint readi()\n{\n")
        self.__write("int x;\ncin >> x;\nreturn x;\n}\n\n")
        
        self.__write("\nfloat readf()\n{\n")
        self.__write("float x;\ncin >> x;\nreturn x;\n}\n\n")
        
        self.__write("\nfloat itof(int x)\n{\n")
        self.__write("return (float)(x);\n}\n\n")
        
        self.__write("\nstring ftos(float x)\n{\n")
        self.__write("return to_string(x);\n}\n\n")
        
        self.__write("\nint stoi(string x)\n{\n")
        self.__write("return stoi(x);\n}\n\n")
        
        self.__write("\nfloat stof(string x)\n{\n")
        self.__write("return stof(x);\n}\n\n")

        self.__write("int main()\n{\n")

    def visit_expr_stmt(self, expr_stmt):
        self.__write(self.__indent())
        expr_stmt.expr.accept(self)
        self.__write(';\n')


    def visit_simple_expr(self, simple_expr): 
        if simple_expr.term is not None:
            simple_expr.term.accept(self)

    def visit_call_rvalue(self, call_rvalue): 
        self.__write(call_rvalue.fun.lexeme)
        
        self.__write('(')
        for i in call_rvalue.args:
            i.accept(self)
        self.__write(')')

    def visit_simple_rvalue(self, simple_rvalue): 
        if simple_rvalue is not None:
            if simple_rvalue.val.tokentype == token.STRINGVAL:
                self.__write('"')
                self.__write(simple_rvalue.val.lexeme)
                self.__write('"')
            else:
                self.__write(simple_rvalue.val.lexeme)

    def visit_var_decl_stmt(self, var_decl): 
        self.__write(self.__indent())
        self.__write("auto ")
        self.__write(var_decl.var_id.lexeme)
        if var_decl.var_type is not None:
            self.__write(var_decl.var_type.lexeme)

        self.__write(" = ")
        var_decl.var_expr.accept(self)
        self.__write(';\n')

    def visit_while_stmt(self, while_stmt):
        self.__write(self.__indent())
        self.__write("while ")
        while_stmt.bool_expr.accept(self)
        self.__write('{')
        self.__write('\n')
        self.indent += 1
        while_stmt.stmt_list.accept(self)

        self.indent -= 1
        self.__write(self.__indent())
        self.__write('}\n')
        if self.indent == 0:
            self.__write('\n')


    def visit_bool_expr(self, bool_expr):
        self.__write('(')
        if bool_expr.negated == True:
            self.__write("not ")
        bool_expr.first_expr.accept(self)
        if bool_expr.bool_rel is not None:
            self.__write(" " + bool_expr.bool_rel.lexeme)
        if bool_expr.second_expr is not None:
            self.__write(" ")
            bool_expr.second_expr.accept(self)
        if bool_expr.bool_connector is not None:
            self.__write( " ")
            self.__write(bool_expr.bool_connector.lexeme)
            bool_expr.rest.accept(self)
        
        self.__write(')')

    def visit_id_rvalue(self, id_rvalue): 
        for i in id_rvalue.path:
           self.__write(i.lexeme)

    def visit_assign_stmt(self, assign_stmt): 
        self.__write(self.__indent())
        assign_stmt.lhs.accept(self)
        self.__write(" = ")
        assign_stmt.rhs.accept(self)
        self.__write(';\n')

    def visit_lvalue(self, lval): 
        for i in lval.path:
            self.__write(i.lexeme)

    def visit_complex_expr(self, complex_expr):
        if type(complex_expr.first_operand) == str:
            self.__write(complex_expr.first_operand)
        else:
            self.__write("(")
            complex_expr.first_operand.accept(self)
        self.__write(" " + complex_expr.math_rel.lexeme + " ")
        complex_expr.rest.accept(self)
        self.__write(")")


    def visit_if_stmt(self, if_stmt): 
        self.__write(self.__indent())
        self.__write("if (")
        if_stmt.if_part.bool_expr.accept(self)

        self.__write('){\n')
        self.indent += 1
        if_stmt.if_part.stmt_list.accept(self)
        for i in if_stmt.elseifs:
            self.__write("else if (")
            i.bool_expr.accept(self)
            self.__write(')\n')
            i.stmt_list.accept(self)
        if if_stmt.has_else == True:
            self.indent -= 1
            self.__write(self.__indent())
            self.__write('else\n')
            self.indent += 1
            if_stmt.else_stmts.accept(self)

        self.indent  -= 1 
        self.__write(self.__indent())
        self.__write('}\n')
        if self.indent == 0:
            self.__write('\n')




