# Author: Luke Hartman
# Course: CPSC 326 - 01, Spring 2019
# Description:
#   This is a Lexer class for MyPL.
#   The class outputs tokens one-by-one
#   from a source file
import token
import error

class Lexer(object):
    def __init__(self, input_stream):
        self.line = 1
        self.column = 0
        self.input_stream = input_stream

    def __peek(self):
        """Returns the next character keeping it in the stream"""
        pos = self.input_stream.tell()
        symbol = self.input_stream.read(1)
        self.input_stream.seek(pos)
        return symbol

    def __read(self):
        """Read 1 character from the stream"""
        return self.input_stream.read(1)

    def __parse_space(self):
        """this function uses the .isspace() function to parse space characters"""
        while self.__peek().isspace():
            if self.__peek() == '\n':
                self.line += 1
                self.column = 0
            else:
                self.column += 1
            self.__read()

    def __parse_line(self):
        ''' This function reads the stream until the next line'''
        while self.__peek() != '\n':
            self.__read()
        self.__read()

    def next_token(self):
        """ Returns the next token to be parsed"""
        self.__parse_space()
        curr_lexeme = ''
        symbol = self.__read()

        # handle single character and <= >= == lexeme cases

        while symbol == '#' or symbol == '\n': # if next char is a comment, parse to next line
            self.__parse_line()
            self.__parse_space()
            self.column = 0
            self.line += 1
            symbol = self.__read()
        curr_lexeme += symbol
        next_symbol = self.__peek()
        self.column += 1

        if symbol == '': # if next char is EOF, return EOS token
            self.column = 0
            return token.Token(token.EOS, curr_lexeme, self.line + 1, self.column)

        elif symbol == ';':
            return token.Token(token.SEMICOLON, curr_lexeme, self.line, self.column)

        elif symbol == '.':
            if next_symbol.isdigit():
                raise error.MyPLError("invalid float value: must start with digit", self.line, self.column)
            return token.Token(token.DOT, curr_lexeme, self.line, self.column)

        elif symbol == ',':
            return token.Token(token.COMMA, curr_lexeme, self.line, self.column)

        elif symbol == ':':
            return token.Token(token.COLON, curr_lexeme, self.line, self.column)

        elif symbol == '=':
            if next_symbol == '=': # handle '==' token
                curr_lexeme += self.__read()
                self.column += 1
                return token.Token(token.EQUAL, curr_lexeme, self.line, self.column)
            else:
                return token.Token(token.ASSIGN, curr_lexeme, self.line, self.column)

        elif symbol == '/':
            return token.Token(token.DIVIDE, curr_lexeme, self.line, self.column)

        elif symbol == '>':
            if next_symbol == '=': # handle '>=' token
                curr_lexeme += self.__read()
                self.column += 1
                return token.Token(token.GREATER_THAN_EQUAL, curr_lexeme, self.line, self.column)
            else:
                return token.Token(token.GREATER_THAN, curr_lexeme, self.line, self.column)
        elif symbol == '!' and next_symbol == '=':
            curr_lexeme += self.__read()
            self.column += 1
            return token.Token(token.NOT_EQUAL, curr_lexeme, self.line, self.column - 1)
        elif symbol == '<':
            if next_symbol == '=':
                curr_lexeme += self.__read()
                self.column += 1
                return token.Token(token.LESS_THAN_EQUAL, curr_lexeme, self.line, self.column)
            else:
                return token.Token(token.LESS_THAN, curr_lexeme, self.line, self.column)

        elif symbol == '(':
            return token.Token(token.LPAREN, curr_lexeme, self.line, self.column)

        elif symbol == ')':
            return token.Token(token.RPAREN, curr_lexeme, self.line, self.column)

        elif symbol == '-':
            return token.Token(token.MINUS, curr_lexeme, self.line, self.column)

        elif symbol == '%':
            return token.Token(token.MODULO, curr_lexeme, self.line, self.column)

        elif symbol == '*':
            return token.Token(token.MULTIPLY, curr_lexeme, self.line, self.column)

        elif symbol == '+':
            return token.Token(token.PLUS, curr_lexeme, self.line, self.column)

        # cases that start with a digit
        elif symbol.isdigit():
            if not next_symbol.isdigit() and next_symbol not in  [';', ',', '%', ')', '\n', ' ', '/', '*', '+', '-', '=', '!', '.']:
                raise error.MyPLError("do not mix ints/floats with other symbol types", self.line, self.column)
            elif int(symbol) == 0 and next_symbol.isdigit():
                raise error.MyPLError("invalid integer value: starts with 0", self.line, self.column)
            else:
                isFloat = False
                index = 0
                while next_symbol not in [';', ',', '%', ')', ']', '\n', ' ', '/', '*', '+', '-', '=', '!', '']:
                    if next_symbol == '.':
                        if isFloat == True:
                            raise error.MyPLError("invalid float: duplicate periods", self.line, self.column)
                        else:
                            isFloat = True
                    curr_lexeme += self.__read()
                    next_symbol = self.__peek()
                    index += 1
                    if curr_lexeme[index] == '.' and not next_symbol.isdigit():
                        raise error.MyPLError("invalid float: cannot end with '.'", self.line, self.column)
                self.column += index
                if isFloat == True:
                    return token.Token(token.FLOATVAL, curr_lexeme, self.line, self.column - index)
                else:
                    return token.Token(token.INTVAL, curr_lexeme, self.line, self.column - index)
        # handle cases with multiple alphanumeric characters
        elif curr_lexeme[0] != '"':
            # append to curr_lexeme till end of token
            while next_symbol not in [';', ':', '(', '[', ')', ']', '.', ',', '%', "+", '\n', '=', '<', '>', '!', ' ', '']:
                curr_lexeme += self.__read()
                next_symbol = self.__peek()
            #return token.Token(token.PLUS, curr_lexeme, self.line, self.column)
            # check the newly formed lexeme for errors
            if curr_lexeme[0] == '_':
                raise error.MyPLError("invalid id: cannot start identifier with '_'", self.line, self.column)
            if curr_lexeme == 'true' or curr_lexeme == "false":
                self.column += len(curr_lexeme) - 1
                return token.Token(token.BOOLVAL, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'int':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.INTTYPE, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'float':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.FLOATTYPE, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'struct':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.STRUCTTYPE, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'string':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.STRINGTYPE, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'or':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.OR, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'and':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.AND, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'not':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.NOT, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'while':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.WHILE, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'do':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.DO, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'if':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.IF, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'then':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.THEN, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'else':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.ELSE, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'elif':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.ELIF, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'end':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.END, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'fun':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.FUN, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'set':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.SET, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'var':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.VAR, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'return':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.RETURN, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'new':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.NEW, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'nil':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.NIL, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            if curr_lexeme == 'bool':
                self.column += len(curr_lexeme) - 1
                return token.Token(token.BOOLTYPE, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
            else:
                self.column += len(curr_lexeme) - 1
                return token.Token(token.ID, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
        # handle cases that appear to be string values
        elif curr_lexeme[0] == '"':
            while next_symbol != '"':
                curr_lexeme += self.__read()
                next_symbol = self.__peek()
                if next_symbol == '\n':
                    raise error.MyPLError("invalid string val: cannot have newline in string", self.line, self.column)

            curr_lexeme += self.__read()
            next_symbol = self.__peek()

            index = 0
            for char in curr_lexeme:
                if char == '"' and index != 0 and index != len(curr_lexeme) - 1:
                    raise error.MyPLError("invalid string val: cannot have \" in string", self.line, self.column)
                index += 1
            self.column += len(curr_lexeme) - 1
            curr_lexeme = curr_lexeme.replace('"', '')
            return token.Token(token.STRINGVAL, curr_lexeme, self.line, self.column - len(curr_lexeme) + 1)
        else:
            raise error.MyPLError("every other error I didn't explicitly hardcode :)", self.line, self.column)
