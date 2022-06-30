from lex import Lex

class Parser:
    def __init__(self, buf):
        self.lex = Lex(buf)
        self.is_over = False
    
    def parse(self):
        self.chunk()

    def chunk(self):
        while not self.is_over:
            self.statement()

    def statement(self):
        token = self.lex.nextToken()
        if token == 'if':
            self.ifstat()
        elif token == 'while':
            self.whilestat()
        elif token == 'for':
            self.forstat()
        elif token == 'break':
            self.breakstat()
        elif token == 'local':
            self.localstat()
        elif token == 'function':
            self.funcstat()
        elif token == 'return':
            self.retstat()
        else:
            self.exprstat()
        

    def ifstat(self):
        pass

    def whilestat(self):
        pass

    def forstat(self):
        pass

    def breakstat(self):
        pass

    def localstat(self):
        pass

    def funcstat(self):
        pass

    def retstat(self):
        pass

    def exprstat(self):
        pass

if __name__ == '__main__':
    f = open('test.lua', 'rb')
    buf = f.read()
    f.close()
    p = Parser(buf)
    p.parse()
    
