from lex import Lex
from lobject import *
from luaconf import *
from lexp import *

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

    def setoneret(self, v: Expdesc):
        if v.expkind == Expdesc.VCALL:
            v.expkind = Expdesc.VNONRELOC
            v.info = 0
        elif v.expkind == Expdesc.VVARARG:
            v.expkind = Expdesc.VRELOCABLE

    def dischargeVars(self, v: Expdesc):
        if v.expkind == Expdesc.VLOCAL:
            v.expkind = Expdesc.VNONRELOC
        elif v.expkind == Expdesc.VUPVAL:
            v.info = self.codeABC(OP_GETUPVAL, 0, v.info, 0)
            v.expkind = Expdesc.VRELOCABLE
        elif v.expkind == Expdesc.VGLOBAL:
            v.info = self.codeABx(OP_GETGLOBAL, 0, v.info)
            v.expkind = Expdesc.VRELOCABLE
        elif v.expkind == Expdesc.VINDEXED:
            v.info = self.codeABC(OP_GETTABLE, 0, v.info, v.aux)
            v.expkind = Expdesc.VRELOCABLE
        elif v.expkind == Expdesc.VVARARG or v.expkind == Expdesc.VCALL:
            self.setoneret(v)
