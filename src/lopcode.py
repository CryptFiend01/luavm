from luaconf import *

class LuaOpCode:
    def __init__(self, code):
        self.code = code

    def GetOpCode(self):
        return self.code & 0x3f

    def GetA(self):
        return (self.code >> 6) & 0xff

    def GetB(self):
        return (self.code >> 23) & 0x1ff

    def GetC(self):
        return (self.code >> 14) & 0x1ff

    def GetBx(self):
        return (self.code >> 14) & 0x3ffff

    def GetsBx(self):
        return self.GetBx() - 0x1ffff

    def toString(self):
        c = self.GetOpCode()
        s = OPNAME[c] + ' ' + str(self.GetA())
        if c in [OP_MOVE,OP_LOADNIL,OP_GETUPVAL,OP_SETUPVAL,OP_UMN,OP_NOT,OP_LEN]:
            s += ' ' + str(self.GetB())
        elif c in [OP_LOADK, OP_GETGLOBAL, OP_SETGLOBAL, OP_CLOSURE]:
            s += ' ' + str(self.GetBx())
        elif c in [OP_FORLOOP, OP_FORPREP]:
            s += ' ' + str(self.GetsBx())
        elif c in [OP_TFORLOOP, OP_TEST]:
            s += ' ' + str(self.GetC())
        #elif c == OP_CLOSE: pass
        else:
            s += ' ' + str(self.GetB()) + ' ' + str(self.GetC())
        return s
