# Author: Luke Hartman
# Course: CPSC 326 - 01, Spring 2019
# Assignment: 2
# Description:
#   This is an error handling class for MyPL
class MyPLError(Exception):

    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        msg = self.message
        line = self.line
        column = self.column
        return 'error: %s at line %i column %i' % (msg, line, column)
