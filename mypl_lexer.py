#!/usr/bin/python3
#
# Author: Kasey Davis
# Course: CPSC 326, Spring 2019
# Assignment: 2
# Description:
#   Tokenizes MyPL code with a lexer
# ----------------------------------------------------------------------


import mypl_token as token
import mypl_error as error


class Lexer(object):

    def __init__(self, input_stream):
        self.line = 1
        self.column = 0
        self.input_stream = input_stream

    def __peek(self):
        pos = self.input_stream.tell()
        symbol = self.input_stream.read(1)
        self.input_stream.seek(pos)
        return symbol

    def __read(self):
        return self.input_stream.read(1)

    def next_token(self):
        symbol = ""
        word = ""

        tokenStartCol = self.column + 1

        if(not self.__peek()):
            return token.Token(token.EOS, "", self.line, tokenStartCol - 1)

        symbol = self.__read()
        word += symbol
        self.column += 1

        # ignore comment lines
        if(symbol == "#"):
            while(self.__peek() != "\n"):
                self.__read()
            self.__read()
            self.column = 0
            self.line += 1
            return self.next_token()

        if(symbol == "\n"):
            self.line += 1
            self.column = 0
            return self.next_token()

        if(symbol.isspace()):
            return self.next_token()

        if(symbol.isalpha()):
            # any later characters, after a first alpha can be alphanumeric or '_'
            while(self.__peek().isalpha() or self.__peek() == "_" or self.__peek().isdigit()):
                symbol = self.__read()
                word += symbol
                self.column += 1

            # All alphabetic-only keywords appear here
            if(word == 'and'):
                return token.Token(token.AND, word, self.line, tokenStartCol)
            elif(word == 'or'):
                return token.Token(token.OR, word, self.line, tokenStartCol)
            elif(word == 'not'):
                return token.Token(token.NOT, word, self.line, tokenStartCol)
            elif(word == 'while'):
                return token.Token(token.WHILE, word, self.line, tokenStartCol)
            elif(word == 'do'):
                return token.Token(token.DO, word, self.line, tokenStartCol)
            elif(word == 'if'):
                return token.Token(token.IF, word, self.line, tokenStartCol)
            elif(word == 'then'):
                return token.Token(token.THEN, word, self.line, tokenStartCol)
            elif(word == 'else'):
                return token.Token(token.ELSE, word, self.line, tokenStartCol)
            elif(word == 'elif'):
                return token.Token(token.ELIF, word, self.line, tokenStartCol)
            elif(word == 'end'):
                return token.Token(token.END, word, self.line, tokenStartCol)
            elif(word == 'fun'):
                return token.Token(token.FUN, word, self.line, tokenStartCol)
            elif(word == 'var'):
                return token.Token(token.VAR, word, self.line, tokenStartCol)
            elif(word == 'set'):
                return token.Token(token.SET, word, self.line, tokenStartCol)
            elif(word == 'return'):
                return token.Token(token.RETURN, word, self.line, tokenStartCol)
            elif(word == 'new'):
                return token.Token(token.NEW, word, self.line, tokenStartCol)
            elif(word == 'nil'):
                return token.Token(token.NIL, word, self.line, tokenStartCol)
            elif(word == 'true' or word == 'false'):
                return token.Token(token.BOOLVAL, word, self.line, tokenStartCol)
            elif(word == 'int'):
                return token.Token(token.INTTYPE, word, self.line, tokenStartCol)
            elif(word == 'bool'):
                return token.Token(token.BOOLTYPE, word, self.line, tokenStartCol)
            elif(word == 'float'):
                return token.Token(token.FLOATTYPE, word, self.line, tokenStartCol)
            elif(word == 'string'):
                return token.Token(token.STRINGTYPE, word, self.line, tokenStartCol)
            elif(word == 'struct'):
                return token.Token(token.STRUCTTYPE, word, self.line, tokenStartCol)

            else:
                return token.Token(token.ID, word, self.line, tokenStartCol)

        if(symbol.isdigit()):
            if(symbol == "0"):
                if(self.__peek().isdigit()):
                    raise error.MyPLError(
                        'unexpected symbol "' + self.__peek() + '"', self.line, tokenStartCol)

            # floats cannot have more than one decimal
            hasDotYet = False
            while(self.__peek().isdigit() or self.__peek() == '.'):
                symbol = self.__read()
                word += symbol
                self.column += 1

                if(symbol == '.'):
                    if(hasDotYet):
                        raise error.MyPLError(
                            'unexpected symbol "' + self.__peek() + '"', self.line, tokenStartCol)
                    hasDotYet = True

            if(symbol == '.'):
                # float ends in '.' and is invalid
                raise error.MyPLError(
                    'missing digit in float value', self.line, self.column + 1)

            if(self.__peek().isalpha()):
                raise error.MyPLError(
                    'unexpected symbol "' + self.__peek() + '"', self.line, tokenStartCol)

            if('.' in word):
                return token.Token(token.FLOATVAL, word, self.line, tokenStartCol)
            else:
                return token.Token(token.INTVAL, word, self.line, tokenStartCol)

        # handle all string types
        if(symbol == '"'):
            while(self.__peek() and self.__peek() != '"' and not self.__peek() == '\n'):
                symbol = self.__read()
                word += symbol
                self.column += 1

            if(not self.__peek() or self.__peek() == '\n'):
                raise error.MyPLError(
                    "reached newline reading string", self.line, self.column)

            elif(self.__peek() == '"'):
                word += self.__read()
                self.column += 1
                return token.Token(token.STRINGVAL, word[1:-1], self.line, tokenStartCol)

        if(symbol == '('):
            return token.Token(token.LPAREN, symbol, self.line, tokenStartCol)

        if(symbol == ')'):
            return token.Token(token.RPAREN, symbol, self.line, tokenStartCol)

        if(symbol == ','):
            return token.Token(token.COMMA, symbol, self.line, tokenStartCol)

        if(symbol == '%'):
            return token.Token(token.MODULO, symbol, self.line, tokenStartCol)

        if(symbol == '+'):
            return token.Token(token.PLUS, symbol, self.line, tokenStartCol)

        if(symbol == '-'):
            return token.Token(token.MINUS, symbol, self.line, tokenStartCol)

        if(symbol == ';'):
            return token.Token(token.SEMICOLON, symbol, self.line, tokenStartCol)

        if(symbol == ':'):
            return token.Token(token.COLON, symbol, self.line, tokenStartCol)

        if(symbol == '*'):
            return token.Token(token.MULTIPLY, symbol, self.line, tokenStartCol)

        if(symbol == '/'):
            return token.Token(token.DIVIDE, symbol, self.line, tokenStartCol)

        if(symbol == '.'):
            return token.Token(token.DOT, symbol, self.line, tokenStartCol)

        if(symbol == '='):
            if(self.__peek() == '='):
                symbol = self.__read()
                word += symbol
                self.column += 1
                return token.Token(token.EQUAL, word, self.line, tokenStartCol)
            else:
                return token.Token(token.ASSIGN, symbol, self.line, tokenStartCol)

        if(symbol == '>'):
            if(self.__peek() == '='):
                symbol = self.__read()
                word += symbol
                self.column += 1
                return token.Token(token.GREATER_THAN_EQUAL, word, self.line, tokenStartCol)
            else:
                return token.Token(token.GREATER_THAN, symbol, self.line, tokenStartCol)

        if(symbol == '<'):
            if(self.__peek() == '='):
                symbol = self.__read()
                word += symbol
                self.column += 1
                return token.Token(token.LESS_THAN_EQUAL, word, self.line, tokenStartCol)
            else:
                return token.Token(token.LESS_THAN, symbol, self.line, tokenStartCol)

        if(symbol == '!'):
            if(self.__peek() == '='):
                symbol = self.__read()
                word += symbol
                self.column += 1
                return token.Token(token.NOT_EQUAL, word, self.line, tokenStartCol)

        raise error.MyPLError('unexpected symbol "' +
                              symbol + '"', self.line, tokenStartCol)
