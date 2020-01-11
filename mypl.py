#!/usr/bin/python3
#
# Author: Luke Hartman
# Description:
#   Simple script to execute the MyPL interpreter.
#----------------------------------------------------------------------
import error
import lexer
import token
import parser
import ast
import type_checker
import interpreter
import sys

def run(file_stream):
    the_lexer = lexer.Lexer(file_stream)
    the_parser = parser.Parser(the_lexer)
    stmt_list = the_parser.parse()
    the_interpreter = interpreter.Interpreter()
    stmt_list.accept(the_interpreter)


def main(filename):
    try:
        file_stream = open(filename, 'r')
        run(file_stream)
        file_stream.close()
    except FileNotFoundError:
        sys.exit('invalid filename %s' % filename)
    except error.MyPLError as e:
        file_stream.close()
        sys.exit(e)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: %s file' % sys.argv[0])
    main(sys.argv[1])
