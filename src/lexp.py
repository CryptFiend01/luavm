from luaconf import *
from lcode import *

class Expdesc:
    VVOID = 0
    VNIL = 1
    VTRUE = 2
    VFALSE = 3
    VK = 4
    VKNUM = 5
    VLOCAL = 6
    VUPVAL = 7
    VGLOBAL = 8
    VINDEXED = 9
    VJMP = 10
    VRELOCABLE = 11
    VNONRELOC = 12
    VCALL = 13
    VVARARG = 14
    def __init__(self, code: LuaCode) -> None:
        self.expkind = Expdesc.VVOID
        self.info = 0
        self.aux = 0
        self.nval = 0
        self.tpos = 0
        self.fpos = 0
        self.code = code

    def init(self, k, i):
        self.expkind = k
        self.info = i
        self.fpos = NO_JUMP
        self.tpos = NO_JUMP

    def setnumber(self, nval):
        self.init(Expdesc.VKNUM, 0)
        self.nval = nval

    def setstring(self, s):
        self.init(Expdesc.VK, self.code.codeString(s))

    def setnil(self):
        self.init(Expdesc.VNIL, 0)

    def setbool(self, b):
        if b:
            self.init(Expdesc.VTRUE, 0)
        else:
            self.init(Expdesc.VFALSE, 0)

    def setdots(self):
        self.init(Expdesc.VVARARG, self.code.codeABC(OP_VARARG, 0, 1, 0))