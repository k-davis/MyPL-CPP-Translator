#!/usr/bin/python3
#
# Author: Kasey Davis
# Course: CPSC 326, Spring 2019
# Assignment: 2
# Description:
#   Tokenizes MyPL code with a lexer
# ----------------------------------------------------------------------


class MyPLError(Exception):

    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        msg = self.message
        line = self.line
        column = self.column
        return 'error: %s at the line %i column %i' % (msg, line, column)
