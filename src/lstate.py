from lobject import *
from luaconf import *

class LuaCallInfo:
    def __init__(self, funci, func, nagrs, nres):
        self.base = 0
        self.funci = funci
        self.func = func    # LuaClosure
        self.savedpc = 0
        self.nresult = nres
        self.nargs = nagrs

    def GetFunc(self):
        return self.func

    def Savedpc(self, pc):
        self.savedpc = pc

    def GetSavedpc(self):
        return self.savedpc

    def SetBase(self, base):
        self.base = base

    def GetArgNum(self):
        return self.nargs

    def GetResultNum(self):
        return self.nresult

    def GetBase(self):
        return self.base

    def GetFunci(self):
        return self.funci

class LuaState:
    def __init__(self):
        self.stack = []
        for i in range(LUA_MINSTACK):
            self.stack.append(Value())
        self.calls = []
        self.call_depth = 0
        self.ci = None

        self.open_upvals = []

        self.base = 0
        self.top = 0        ## offset to self.base
        self.savedpc = 0
        self.is_print = False

    def setPrint(self, is_print):
        self.is_print = is_print

    def GetTop(self):
        return self.stack[self.top]

    def GetTopi(self):
        return self.top

    def GetBasei(self):
        return self.base

    def GetFixStack(self, i):
        return self.stack[i]

    def GetStack(self, i):
        return self.stack[self.base + i]

    def GetAllStack(self):
        return self.stack

    def SetBasei(self, base):
        if self.is_print:
            print("base->" + str(base))
        self.base = base

    def SetFixStack(self, i, val):
        self.stack[i] = val

    def SetStack(self, i, val):
        self.stack[self.base + i] = val

    def CopyFixStack(self, src, dst):
        if src == dst:
            return
        
        if src >= len(self.stack) or dst >= len(self.stack):
            print("out of stack range.")
            return
        self.stack[dst].Copy(self.stack[src])

    def CopyStack(self, src, dst):
        self.CopyFixStack(src + self.base, dst + self.base)

    def LoadProto(self, p):
        cl = LuaClosure(p, {})
        self.stack[self.top].SetClosure(cl)
        self.top += 1

    def GetCurrentCall(self):
        return self.ci

    def GetCurrentCallRetNum(self):
        return self.ci.GetResultNum()

    def GetSavedpc(self):
        return self.savedpc

    def Savedpc(self, pc):
        self.savedpc = pc

    def FindUpval(self, level):
        lv = level + self.base
        for val in self.open_upvals:
            if val.GetStack() == lv:
                v = self.GetFixStack(val.GetStack())
                return v.GetValue()
            elif val.GetStack() < lv:
                break
        
        upv = LuaUpVal()
        upv.SetStack(lv)
        self.open_upvals.append(upv)
        return upv

    def CloseUpval(self, level):
        n = 0
        for i in range(len(self.open_upvals) -1, -1, -1):
            val = self.open_upvals[i]
            if val.GetStack() < level:
                break
            n += 1
        for i in range(n):
            self.open_upvals.pop(-1)

    def PreCall(self, funci, nargs, nres):
        cur_ci = self.GetCurrentCall()
        if cur_ci:
            cur_ci.Savedpc(self.savedpc)

        if self.is_print:
            print("PreCall funci:" + str(funci) + ", base:" + str(self.base))
        base = self.base

        fv = self.GetStack(funci)
        func = fv.GetValue()
        proto = func.GetProto()
        if not proto.IsVarargs():
            self.SetBasei(self.base + funci + 1)
        else:
            self.SetBasei(self.base + funci + nargs + 1)
        ci = LuaCallInfo(funci + base, func, nargs, nres)
        ci.SetBase(self.base)
        self.calls.append(ci)
        self.ci = self.calls[-1]
        self.savedpc = 0

    def PosCall(self, resi):
        ## copy result to current call begin pos and replace from the pos of func and set the rest pos to nil
        ci = self.ci
        self.calls.pop(-1)
        
        funci = ci.GetFunci()
        max_resi = funci + ci.GetResultNum()
        resi = self.base + resi ## trans resi to fix pos.

        if len(self.calls) > 0:
            self.ci = self.calls[-1]
            self.savedpc = self.ci.GetSavedpc()
            self.SetBasei(self.ci.GetBase())
        else:
            self.ci = None
        wanted_res = resi - funci + 1
        if self.is_print:
            print("basei=" + str(self.base))
            print("funci=" + str(funci) + " val=" + self.GetFixStack(funci).toString())
            print("resi=" + str(resi) + " val=" + self.GetFixStack(resi).toString())
            print("wanted_res=" + str(wanted_res))
        for i in range(wanted_res):
            if funci >= max_resi:
                self.SetFixStack(funci, Value())
            else:
                self.CopyFixStack(resi, funci)
                self.top = funci - self.base
                resi += 1
            funci += 1
        return wanted_res + 1

    def ShowStack(self):
        if not self.is_print:
            return
        print("-----------Stack----------")
        for v in self.stack:
            print("|  %s  |" % v.toString())
        print("--------------------------")
