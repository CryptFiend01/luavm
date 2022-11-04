from luaconf import *

class Lex:
    def __init__(self, buf):
        self.buff = buf
        self.line_no = 1
        self.current = 0
        self.num_val = 0
        self.str_val = ''
        self.reserves = ['function', 'local', 'end', 'if',
                         'then', 'do', 'else', 'elseif', 'return',
                         'while', 'break', 'until', 'true', 'false',
                         'nil', 'not', 'or', 'and', 'repeat', 'in']
        self.error = ''
        self.token = 'TK_NONE'
        self.next = None

    def start(self):
        self.getC()

    def getLineNo(self):
        return self.line_no

    def getError(self):
        return self.error

    def getNum(self):
        return self.num_val

    def getStr(self):
        return self.str_val

    def getC(self):
        if self.current >= len(self.buff):
            return ''
        c = self.buff[self.current]
        self.current += 1
        return c

    def isEnd(self):
        return self.current >= len(self.buff)

    def skipComment(self):
        c = self.getC()
        while c != '\n':
            c = self.getC()
        self.getC()
        self.line_no += 1

    def loadString(self, pre):
        s = ''
        c = self.getC()
        if pre != '[[':
            while c != pre:
                s += c
                if c == '\n' or c == '\r':
                    self.error = 'Error string at line ' + str(self.line_no)
                    return ''
                c = self.getC()
        else:
            while True:
                if c == ']':
                    d = self.getC()
                    if d == ']':
                        break
                    else:
                        s += c
                        c = d
                s += c
                if c == '\n':
                    self.line_no += 1
                c = self.getC()
        self.getC()
        return s

    def loadName(self, start):
        s = start
        c = self.getC()
        while c.isalnum() or c == '_':
            s += c
            c = self.getC()
        return s

    def loadNumber(self, start):
        s = start
        c = self.getC()
        etimes = 0
        dottimes = 0
        while True:
            if c == '.':
                if dottimes == 1:
                    self.error = 'Error number symbol . at line ' + str(self.line_no)
                    return 0
                s += c
                dottimes += 1
            elif c == 'E' or c == 'e':
                if etimes == 1:
                    self.error = 'Error number symbol e at line ' + str(self.line_no)
                    return 0
                s += c
                etimes += 1
                c = self.getC()
                if c == '-' or c.isdigit():
                    s += c
                else:
                    self.error = 'Error number symbol e at line ' + str(self.line_no)
                    return 0
            elif c.isdigit():
                s += c
            else:
                break
            c = self.getC()
        return float(s)

    def getToken(self):
        return self.token

    def nextToken(self):
        if self.next != None:
            self.token = self.next[0]
            if self.token == TK_NUMBER:
                self.num_val = self.next[1]
            elif self.token == TK_NAME or self.token == TK_STRING:
                self.str_val = self.next[1]
            self.next = None
        else:
            self.token = self.__nextToken()
        return self.token

    def skipToken(self, t):
        self.next = self.__nextToken()
        if self.next[0] == t:
            self.next = None
            return True
        else:
            return False

    def __nextToken(self):
        self.error = ''
        c = self.buff[self.current - 1]
        #print 'c=', ord(c), '|'
        while c == ' ' or c == "\t" or c == "\n" or c == "\r" or c == '':
            if c == '\n':
                self.line_no += 1
            elif c == '':
                return 'TK_NONE', None
            c = self.getC()

        if c == '=':
            c = self.getC()
            if c == '=':
                self.getC()
                return 'TK_EQ', None
            else:
                return '='
        elif c == '-':
            c = self.getC()
            if c == '-':
                self.skipComment()
                return 'TK_COMMENT', None
            elif c.isdigit():
                num_val = -self.loadNumber(c)
                return 'TK_NUMBER', num_val
            else:
                return c, None
        elif c == '[':
            c = self.getC()
            if c == '[':
                str_val = self.loadString('[[')
                return 'TK_STRING', str_val
            else:
                return '[', None
        elif c == '~':
            c = self.getC()
            if c == '=':
                self.getC()
                return 'TK_NE', None
            else:
                self.error = 'Error ~, expect ~= at line ' + str(self.line_no)
                return 'TK_NONE', None
        elif c == '<':
            c = self.getC()
            if c == '=':
                self.getC()
                return 'TK_LE', None
            else:
                return '<', None
        elif c == '>':
            c = self.getC()
            if c == '=':
                self.getC()
                return 'TK_GE', None
            else:
                return '>', None
        elif c == '.':
            c = self.getC()
            if c == '.':
                c = self.getC()
                if c != '.':
                    return 'TK_CONCAT', None
                else:
                    self.getC()
                    return '...', None
            else:
                return c, None
        elif c == '"' or c == "'":
            str_val = self.loadString(c)
            return 'TK_STRING', str_val
        elif c.isalpha() or c == '_':
            str_val = self.loadName(c)
            if str_val in self.reserves:
                return self.str_val, None
            else:
                return 'TK_NAME', str_val
        elif c.isdigit():
            num_val = self.loadNumber(c)
            return 'TK_NUMBER', num_val
        else:
            self.getC()
            return c, None

def loadLua(fname):
    f = open(fname, 'rb')
    buf = f.read()
    f.close()

    line_no = 1
    line = ''
    lex = Lex(buf)
    lex.start()
    while True:
        token = lex.nextToken()
        if lex.getError() != '':
            print(lex.getError())
            break

        if lex.getLineNo() > line_no:
            print(line)
            line_no = lex.getLineNo()
            line = ''
        
        line += token
        if token == 'TK_NAME' or token == 'TK_STRING':
            line += '<' + lex.getStr() + '> '
        elif token == 'TK_NUMBER':
            line += '<' + str(lex.getNum()) + '> '
        else:
            line += ' '
        
        if token == 'TK_NONE':
            break

if __name__ == '__main__':
    loadLua('test.lua')
