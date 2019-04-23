#!/usr/bin/python3
#
# Author Kasey Davis
# Assignment: 7
# Description:
#   Simple script to execute the MyPL interpreter.
# ----------------------------------------------------------------

import mypl_error as error
import mypl_lexer as lexer
import mypl_token as token
import mypl_parser as parser
import mypl_ast as ast
import mypl_type_checker as type_checker
import mypl_name_mangler as name_mangler
import mypl_translator as translator
import sys
import os


def main(filename):
    try:
        print_file = '__temp_file.cpp'
        file_stream = open(filename, 'r')
        print_stream = open(print_file, 'w')    
        temp_stream = open("__translated_source.cpp", "w")
        hw7(file_stream, print_stream, temp_stream)
        file_stream.close()
        temp_stream.close()
        files_together(print_file, "__translated_source.cpp")
    except FileNotFoundError:
        sys.exit('invalid filename %s' % filename)
    except error.MyPLError as e:
        file_stream.close()
        sys.exit(e)

def files_together(print_stream, append_stream):
    end_of_file = open(print_stream, "r")
    app_stream = open(append_stream, "a")

    for line in end_of_file:
        app_stream.write(line)

    end_of_file.close()
    app_stream.close()
    os.remove("__temp_file.cpp")
    

def hw7(file_stream, print_stream,temp_stream):
    the_lexer = lexer.Lexer(file_stream)

    the_parser = parser.Parser(the_lexer)
    stmt_list = the_parser.parse()
    
    the_type_checker = type_checker.TypeChecker()
    stmt_list.accept(the_type_checker)

    the_name_mangler = name_mangler.NameMangler()
    stmt_list.accept(the_name_mangler)

    the_translator = translator.TranslationVisitor(print_stream, temp_stream)
    stmt_list.accept(the_translator)
    
    finish_file(print_stream)


def finish_file(print_stream):
    print_stream.write("return 0;\n")
    print_stream.write("}")
    print_stream.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: %s file' % sys.argv[0])
    main(sys.argv[1])






