import luaconf
from luaconf import LUA_TNUMBER, isnumber

class Value:
    def __init__(self):
        self.tt = luaconf.LUA_TNIL
        self.val = None

    def GetType(self):
        return self.tt

    def SetNil(self, n):
        self.tt = luaconf.LUA_TNIL
        self.val = None

    def SetNumber(self, n):
        self.tt = luaconf.LUA_TNUMBER
        self.val = n

    def SetBoolean(self, b):
        self.tt = luaconf.LUA_TBOOLEAN
        self.val = b

    def SetString(self, s):
        self.tt = luaconf.LUA_TSTRING
        self.val = s

    def SetTable(self, tb):
        self.tt = luaconf.LUA_TTABLE
        self.val = tb

    def SetUpval(self, upval):
        self.tt = luaconf.LUA_TUPVAL
        self.val = upval

    def SetProto(self, proto):
        self.tt = luaconf.LUA_TPROTO
        self.val = proto

    def SetClosure(self, cl):
        self.tt = luaconf.LUA_TFUNCTION
        self.val = cl

    def IsNil(self):
        return self.tt == luaconf.LUA_TNIL

    def IsNumber(self):
        return self.tt == luaconf.LUA_TNUMBER

    def IsString(self):
        return self.tt == luaconf.LUA_TSTRING

    def IsFunction(self):
        return self.tt == luaconf.LUA_TFUNCTION

    def IsBoolean(self):
        return self.tt == luaconf.LUA_TBOOLEAN

    def IsTable(self):
        return self.tt == luaconf.LUA_TTABLE

    def IsProto(self):
        return self.tt == luaconf.LUA_TPROTO

    def IsUpval(self):
        return self.tt == luaconf.LUA_TUPVAL

    def GetValue(self):
        return self.val

    def Copy(self, val):
        self.tt = val.tt
        self.val = val.val

    def toString(self):
        if self.tt == luaconf.LUA_TNIL:
            return "nil"
        elif self.tt == luaconf.LUA_TNUMBER:
            return str(self.val)
        elif self.tt == luaconf.LUA_TSTRING:
            return str(self.val)
        elif self.tt == luaconf.LUA_TBOOLEAN:
            if not self.val:
                return "False"
            else:
                return "True"
        elif self.tt == luaconf.LUA_TTABLE:
            return "table"
        elif self.tt == luaconf.LUA_TFUNCTION:
            return "function"
        elif self.tt == luaconf.LUA_TUPVAL:
            return "upval"
        elif self.tt == luaconf.LUA_TPROTO:
            return "proto"
        else:
            return "Object"

def EqualV(v1, v2):
    if v1 is v2:
        return True
    return v1.GetType() == v2.GetType() and v1.GetValue() == v2.GetValue()

def LessThenV(v1, v2):
    if v1.GetType() != v2.GetType():
        print("Can't compare type %d with %d" % (v1.GetType(), v2.GetType()))
        return False
    if v1.GetType() == luaconf.LUA_TNUMBER:
        return v1.GetValue() < v2.GetValue()
    elif v1.GetType() == luaconf.LUA_TSTRING:
        return v1.GetValue() < v2.GetValue()
    else:
        print("Can't compare type %d" % (v1.GetType()))
        return False

def LessEqualV(v1, v2):
    if v1.GetType() != v2.GetType():
        print("Can't compare type %d with %d" % (v1.GetType(), v2.GetType()))
        return False
    if v1.GetType() == luaconf.LUA_TNUMBER:
        return v1.GetValue() <= v2.GetValue()
    elif v1.GetType() == luaconf.LUA_TSTRING:
        return v1.GetValue() <= v2.GetValue()
    else:
        print("Can't compare type %d" % (v1.GetType()))
        return False

class LuaObject:
    def __init__(self):
        self.tt = luaconf.LUA_TNIL

class LuaProto:
    def __init__(self):
        self.consts = []        ## Value
        self.codes = []         ## int
        self.sub_protos = []
        self.line_infos = []
        self.local_vars = []
        self.upval_names = []
        self.nparams = 0
        self.nups = 0
        self.is_varargs = False

    def GetConst(self, i):
        return self.consts[i]

    def GetCode(self, i):
        return self.codes[i]

    def GetCodeCount(self):
        return len(self.codes)

    def GetSubProto(self, i):
        return self.sub_protos[i]

    def GetUpvalNum(self):
        return self.nups

    def IsVarargs(self):
        return self.is_varargs

    def PushCode(self, code):
        self.codes.append(code)

    def PushConst(self, k):
        self.consts.append(k)

    def PushSubProto(self, p):
        self.sub_protos.append(p)

    def ShowCodes(self):
        print(self.codes)

    def ShowConst(self):
        print("---------Const----------")
        for k in self.consts:
            print(k.toString())
        print("------------------------")

class LuaUpVal:
    def __init__(self):
        self.val = None
        self.stack = -1

    def SetStack(self, stack):
        self.stack = stack
        self.val = None

    def SetValue(self, val):
        self.val = val
        self.stack = -1

    def GetStack(self):
        return self.stack

    def GetValue(self):
        return self.val

class LuaClosure:
    def __init__(self, proto, env):
        self.proto = proto
        self.upvals = [LuaUpVal()] * proto.GetUpvalNum()
        self.env = env

    def AddUpval(self, upval):
        self.upvals.append(upval)

    def GetUpvalCount(self):
        return len(self.upvals)

    def GetUpval(self, i):
        return self.upvals[i]

    def GetProto(self):
        return self.proto

    def Env(self):
        return self.env

    def GetEnv(self, key):
        return self.env.get(key)

    def SetEnv(self, key, val):
        self.env[key] = val

class LuaTable:
    def __init__(self):
        self.kv = {}
    
    def Get(self, key):
        assert(key != None)
        if not isinstance(key, Value):
            vkey = toValue(key)
            if vkey.IsNil():
                return None
            return self.kv.get(vkey)
        else:
            return self.kv.get(key)

    def Set(self, key, val):
        assert(key != None)
        if not isinstance(key, Value):
            vkey = toValue(key)
            if vkey.IsNil():
                return None
            self.kv[vkey] = val
        else:
            self.kv[key] = val

    def GetCount(self):
        n = 0
        for k, v in self.kv.items():
            if isinstance(k, int) and n < k:
                n = k
        return n

class LocalVar:
    def __init__(self):
        self.name = ""
        self.startpc = 0
        self.endpc = 0

def toValue(val):
    v = Value()
    if isinstance(val, int) or isinstance(val, float):
        v.SetNumber(val)
    elif isinstance(val, str):
        v.SetString(val)
    elif isinstance(val, bool):
        v.SetBoolean(val)
    elif isinstance(val, LuaProto):
        v.SetProto(val)
    elif isinstance(val, LuaClosure):
        v.SetClosure(val)
    elif isinstance(val, LuaUpVal):
        v.SetUpval(val)
    elif isinstance(val, LuaTable):
        v.SetTable(val)
    return v

