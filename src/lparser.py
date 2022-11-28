from lex import Lex
from lobject import LuaProto, FuncState
from luaconf import *
from lexp import *
import os

PRIORITY = [[6,6], [6,6], [7,7], [7,7], [7,7],
            [10,9], [5,4],
            [3,3], [3,3],
            [3,3], [3,3], [3,3], [3,3],
            [2,2], [1,1]]
UNARY_PRIORITY = 8

# 解析代码文件，将其转化为op码
class Parser:
    def __init__(self, buf):
        self.lex = Lex(buf)
        self.unoprs = ['not', '-', '#']
        self.binoprs = ['+', '-', '*', '/', '%', '^', TK_CONCAT, TK_NE, TK_EQ, '<', TK_LE, '>', TK_GE, 'and', 'or']
        self.token = ''
        self.code = LuaCode()
        self.fnc = None
        self.fncStack = []

    def symbolError(self, err):
        print("[line %d token %s]: " % (self.lex.line_no, self.token) + err)
        os.abort()
    
    def parse(self):
        # 1. 每一个函数开头自己获取当前处理所需要的token
        # 2. 结尾的时候不能调用nextToken获取下一个token，最多只能检测下一个token
        # 3. 前后都不调用nextToken的函数前面加上 _ 进行标记
        # 4. 中间调用完成完整语法块的情况不属于第三种情况
        self.openfunc()
        self.chunk()
        self.closefunc()
        return self.fnc.proto

    def block(self):
        self.openfunc()
        self.chunk()
        self.closefunc()

    def chunk(self):
        is_over = False
        while not is_over:
            is_over = self.statement()
            self.lex.skipToken(';')

    def body(self, v: Expdesc):
        pass

    def openfunc(self):
        if self.fnc != None:
            self.fncStack.append(self.fnc)
        self.fnc = FuncState()
        self.fnc.open()
        self.code.setFunc(self.fnc)

    def closefunc(self):
        p = self.func.proto
        self.fnc.close()
        if len(self.fncStack) > 0:
            self.fnc = self.fncStack.pop()
            self.fnc.proto.PushSubProto(p)
            self.code.setFunc(self.fnc)

    def statement(self):
        self.token = self.lex.nextToken()
        token = self.token
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

    def constructor(self, v: Expdesc):
        pass

    def markupval(self, v: Expdesc):
        pass

    def indexupvalue(self, fs: FuncState, v: Expdesc):
        p = fs.proto
        def setExp(v, i):
            v.info = i
            v.expkind = Expdesc.VUPVAL
        vname = self.lex.getStr()
        for i in range(len(p.upval_names)):
            if p.upval_names[i] == vname:
                setExp(v, i)
                return
        p.upval_names.append(vname)

    def searchvar(self, fs: FuncState, vname):
        p = fs.proto
        for i in range(p.local_vars):
            if p.local_vars[i].name == vname:
                return i
        return -1

    def singlevaraux(self, fn, v: Expdesc):
        if fn > len(self.fncStack):
            v.setglobal(self.lex.getStr())
        else:
            if fn == 0:
                fs = self.fnc
            else:
                fs = self.fncStack[len(self.fncStack)-fn]
            vn = self.searchvar(fs, self.lex.getStr())
            if vn >= 0:
                v.setlocal(vn)
                if fn == 0:
                    self.markupval(v)
            else:
                fn2 = fn + 1
                if fn2 > len(self.fncStack):
                    self.singlevaraux(fn2, v)
                else:
                    self.indexupvalue(fs, v)

    def singlevar(self, v: Expdesc):
        self.singlevaraux(0, v)

    def prefixexp(self, v: Expdesc):
        if self.token == '(':
            self.expr(v)
            if self.lex.nextToken() != ')':
                self.symbolError("( is not match.")
            self.code.dischargeVars(v)
        elif self.token == TK_NAME:
            self.singlevar(v)
        else:
            self.symbolError("unexpected symbol")

    def primaryexp(self, v: Expdesc):
        self.prefixexp(v)
        while True:
            if self.token == '.':
                pass
            elif self.token == '[':
                pass
            elif self.token == ':':
                pass
            elif self.token in ['(', TK_STRING, '{']:
                pass
            else:
                return

    def _simpleexp(self, v: Expdesc):
        if self.token == TK_NUMBER:
            v.setnumber(self.lex.getNum())
        elif self.token == TK_STRING:
            v.setstring(self.lex.getStr())
        elif self.token == 'nil':
            v.setnil()
        elif self.token == 'true':
            v.setbool(True)
        elif self.token == 'false':
            v.setbool(False)
        elif self.token == '...':
            v.setdots()
        elif self.token == '{':
            self.constructor(v)
        elif self.token == 'function':
            self.body(v)
        else:
            self.primaryexp(v)
        return v

    def subexpr(self, v: Expdesc, priot):
        self.token = self.lex.nextToken()
        if self.token not in self.unoprs:
            self.subexpr(v, UNARY_PRIORITY)
        else:
            self._simpleexp(v)
        
        self.token = self.lex.nextToken()

        def getBinOp():
            if self.token not in self.binoprs:
                return -1
            return self.binoprs.index(self.token)
        
        op = getBinOp()
        while op != -1 and PRIORITY[op][0] > priot:
            v2 = Expdesc(self.code)
            nextop = self.subexpr(v2, PRIORITY[op][1])
            op = nextop
        return op

    def expr(self, v: Expdesc):
        self.subexpr(v, 0)

    def cond(self):
        v = Expdesc(self.code)
        self.expr(v)

    def test_then_block(self):
        condexit = self.cond()
        return condexit

    def ifstat(self):
        self.test_then_block()
        while self.lex.token == 'elseif':
            self.test_then_block()
        if self.lex.token == 'else':
            self.block()
        else:
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
    
