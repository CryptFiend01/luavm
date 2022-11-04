from lex import Lex
from lobject import *

SIZE_C	= 9
SIZE_B	= 9
SIZE_Bx	= (SIZE_C + SIZE_B)
SIZE_A	= 8
SIZE_OP	= 6
POS_OP = 0
POS_A = (POS_OP + SIZE_OP)
POS_C = (POS_A + SIZE_A)
POS_B = (POS_C + SIZE_C)
POS_Bx = POS_C

def create_abc(o, a, b, c):
    return ((int(o) << POS_OP) | (int(a) << POS_A) | (int(b) << POS_B) | (int(c) << POS_C))

def create_abx(o, a, bc):
    return ((int(o) << POS_OP) | (int(a) << POS_A) | (int(bc) << POS_Bx))

class LuaCode:
    def __init__(self, lex : Lex) -> None:
        self.lex = lex
        self.fnc = None

    def setFunc(self, fnc: FuncState):
        self.fnc = fnc

    def code(self, c, line):
        p = self.fnc.proto
        # dischargejpc
        p.PushCode(c)
        p.PushLine(line)

    def codeABC(self, opc, a, b, c):
        self.code(create_abc(opc, a, b, c), self.lex.line_no)

    def codeABx(self, opc, a, bc):
        self.code(create_abx(opc, a, bc), self.lex.line_no)

    def addK(self, k, v):
        self.fnc.stack.append(k)

    def codeString(self, s):
        return 0

    def codeNum(self, n):
        return 0
