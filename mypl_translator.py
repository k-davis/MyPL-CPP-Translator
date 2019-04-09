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

    def __basics(self):
        self.__write("#include <iostream>\n")
        self.__write("\n")
        self.__write("using namespace std;\n")
        self.__write("void print(string x)\n{\n")
        self.__write("cout << x << endl;\n}\n")
        self.__write("int main()\n{")
        self.__write("\n")
        self.__write("return 0;\n")
        self.__write("}")