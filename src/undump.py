from luaconf import LUA_TBOOLEAN, LUA_TNIL, LUA_TSTRING
from lobject import *
import struct

class LuaUndump:
    def __init__(self):
        self.buf = None
        self.offset = 0

    def undump(self, name):
        f = open(name, "rb")
        self.buf = f.read()
        f.close()
        self.offset = 0
        self.readHeader()
        return self.readFunction()

    def readHeader(self):
        self.offset += 12

    def readString(self):
        n = self.readInt()
        s = struct.unpack_from("%ds" % n, self.buf, self.offset)
        self.offset += n
        return s[0]

    def readInt(self):
        n = struct.unpack_from("i", self.buf, self.offset)
        self.offset += 4
        return n[0]

    def readNumber(self):
        n = struct.unpack_from("d", self.buf, self.offset)
        self.offset += 8
        return n[0]

    def readByte(self):
        c = struct.unpack_from("b", self.buf, self.offset)
        self.offset += 1
        return c[0]

    def readFunction(self):
        p = LuaProto()
        source = self.readString()
        line_defined = self.readInt()
        last_line_defined = self.readInt()
        p.nups = self.readByte()
        p.nparams = self.readByte()
        p.is_varargs = self.readByte() != 0
        max_stack_size = self.readByte()
        
        self.readCode(p)
        self.readConst(p)
        self.readSubProto(p)
        self.readDebug(p)
        return p

    def readCode(self, p):
        n = self.readInt()
        for i in range(n):
            code = self.readInt()
            p.PushCode(code)

    def readConst(self, p):
        n = self.readInt()

        for i in range(n):
            tag = self.readByte()
            v = Value()
            if tag == LUA_TBOOLEAN:
                b = self.readByte()
                v.SetBoolean(b != 0)
            elif tag == LUA_TNUMBER:
                n = self.readNumber()
                v.SetNumber(n)
            elif tag == LUA_TSTRING:
                s = self.readString()
                v.SetString(s)
            elif tag != LUA_TNIL:
                print("Error tag type " + str(tag))
            p.PushConst(v)

    def readSubProto(self, p):
        n = self.readInt()
        for i in range(n):
            f = self.readFunction()
            p.PushSubProto(f)

    def readDebug(self, p):
        n = self.readInt()
        if n <= 0:
            return
        for i in range(n):
            p.line_infos.append(self.readInt())

        n = self.readInt()
        for i in range(n):
            v = LocalVar()
            v.name = self.readString()
            v.startpc = self.readInt()
            v.endpc = self.readInt()
            p.local_vars.append(v)

        n = self.readInt()
        for i in range(n):
            p.upval_names.append(self.readString())