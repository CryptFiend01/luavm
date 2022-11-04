from lobject import *
from luaconf import *
from lopcode import LuaOpCode

def isConst(c):
    return (c & 0x100) != 0

def rkb(code, state, proto):
    b = code.GetB()
    if isConst(b):
        return proto.GetConst(b & 0xff)
    else:
        return state.GetStack(b)

def rkc(code, state, proto):
    c = code.GetC()
    if isConst(c):
        return proto.GetConst(c & 0xff)
    else:
        return state.GetStack(c)

def arith(state, code, proto, func):
    b = rkb(code, state, proto)
    c = rkc(code, state, proto)
    if isnumber(b) and isnumber(c):
        state.SetStack(code.GetA(), toValue(func(b.GetValue(), c.GetValue())))
    else:
        state.SetStack(code.GetA(), toValue(func(float(b.GetValue()), float(c.GetValue()))))

def printd(s):
    #print(s)
    pass

class LuaVm:
    def __init__(self, state):
        self.state = state
        self.calls = 0
        self.reset()

    def reset(self):
        self.savedpc = 0
        self.pc = 0
        self.func = None
        self.p = None

    def getCalls(self):
        return self.calls
    
    def enterCall(self):
        self.pc = self.state.GetSavedpc()
        ci = self.state.GetCurrentCall() # LuaCallInfo
        self.func = ci.GetFunc()     # LuaClosure
        self.p = self.func.GetProto()     # LuaProto
        return (self.pc, self.func, self.p)

    def execute(self):
        #self.enterCall()
        while True:
            self.executeOnce()
            if self.calls == 0:
                break

    def executeOnce(self):
        if self.calls == 0:
            self.calls = 1
            self.enterCall()
        pc, func, p = self.pc, self.func, self.p
        state = self.state
        c = p.GetCode(pc)
        code = LuaOpCode(c)
        printd("(" + str(pc) +")[Code:"+str(c)+"] op: " + str(code.GetOpCode()) + ", A: " + str(code.GetA()) + ", B: " + str(code.GetB()) + ", C: " + str(code.GetC()) + ", Bx: " + str(code.GetBx()) + ", sBx: " + str(code.GetsBx()))
        pc += 1

        oc = code.GetOpCode()
        if oc == OP_MOVE:
            printd("move [%d %d]" % (code.GetA(), code.GetB()) + state.GetStack(code.GetB()).toString() + " to " + str(code.GetA()))
            state.CopyStack(code.GetB(), code.GetA())
        elif oc == OP_LOADK:
            state.SetStack(code.GetA(), p.GetConst(code.GetBx()))
            printd("load const [%d]" % (code.GetBx()) + p.GetConst(code.GetBx()).toString() + " to " + str(code.GetA()))
        elif oc == OP_LOADBOOL:
            state.SetStack(code.GetA(), toValue(code.GetB()))
            if code.GetC() != 0:
                pc += 1
        elif oc == OP_GETGLOBAL:
            kbx = p.GetConst(code.GetBx())
            printd("get global %d %s" % (code.GetA(), kbx.toString()))
            state.SetStack(code.GetA(), func.GetEnv(kbx))
        elif oc == OP_SETGLOBAL:
            kbx = p.GetConst(code.GetBx())
            env_val = Value()
            env_val.Copy(state.GetStack(code.GetA()))
            printd("set global %s=%s" % (kbx.toString(), env_val.toString()))
            func.SetEnv(kbx, env_val)
        elif oc == OP_GETTABLE:
            v = state.GetStack(code.GetB())
            if v.IsTable():
                tb = v.GetValue()
                val = tb.Get(rkc(code, state, p))
                state.SetStack(code.GetA(), val)
            else:
                printd("target address is not table.")
        elif oc == OP_SETTABLE:
            v = state.GetStack(code.GetA())
            if v.IsTable():
                tb = v.GetValue()
                key = rkb(code, state, p)
                val = rkc(code, state, p)
                t = tb.Get(key)
                if t:
                    t.Copy(val)
                else:
                    tb.Set(key, val)
                printd("set table<%d>[%s]=%s" % (code.GetA(), key.toString(), val.toString()))
            else:
                printd("target address is not table.")
        elif oc == OP_NEWTABLE:
            state.SetStack(code.GetA(), toValue(LuaTable()))
        elif oc == OP_SETLIST:
            n = code.GetB()
            c = code.GetC()
            if n == 0:
                n = LUA_MINSTACK - code.GetA() - 1
            if c == 0:
                c = p.GetCode(pc)
                pc += 1
                printd("pc->" + str(pc))
            h = state.GetStack(code.GetA()).GetValue()
            last = (c - 1) * FPF + n
            while n > 0:
                val = state.GetStack(code.GetA() + n)
                h.Set(last, val)
                last -= 1
                n -= 1
        elif oc == OP_ADD:
            arith(state, code, p, lambda x, y: x + y)
        elif oc == OP_SUB:
            arith(state, code, p, lambda x, y: x - y)
        elif oc == OP_MUL:
            arith(state, code, p, lambda x, y: x - y)
        elif oc == OP_DIV:
            arith(state, code, p, lambda x, y: x / y)
        elif oc == OP_MOD:
            arith(state, code, p, lambda x, y: x % y)
        elif oc == OP_POW:
            arith(state, code, p, lambda x, y: pow(x, y))
        elif oc == OP_UMN:
            b = code.GetB()
            if isnumber(b):
                state.SetStack(code.GetA(), toValue(-b))
            else:
                state.SetStack(code.GetA(), toValue(-float(b)))
        elif oc == OP_NOT:
            rb = state.GetStack(code.GetB())
            state.SetStack(code.GetA(), toValue(not rb.GetValue()))
        elif oc == OP_LEN:
            rb = state.GetStack(code.GetB())
            v = rb.GetValue()
            if rb.IsTable():
                state.SetStack(code.GetA(), toValue(v.GetCount()))
            elif rb.IsString():
                state.SetStack(code.GetA(), toValue(len(v)))
            else:
                printd("Can't getn with type: %d" % rb.GetType())
        elif oc == OP_CLOSURE:
            sp = p.GetSubProto(code.GetBx())
            cl = LuaClosure(sp, func.Env())
            for i in range(sp.GetUpvalNum()):
                nc = LuaOpCode(pc)
                if nc.GetOpCode() == OP_GETUPVAL:
                    cl.AddUpval(func.GetUpval(nc.GetB()))
                elif nc.GetOpCode() == OP_MOVE:
                    cl.AddUpval(state.FindUpval(nc.GetB()))
                pc += 1
            printd("set closure at [" + str(code.GetA()) + "]")
            state.SetStack(code.GetA(), toValue(cl))
        elif oc == OP_CALL:
            state.Savedpc(pc)
            nparam = code.GetB() - 1
            if nparam < 0:
                nparam = 0
            nres = code.GetC() - 1
            printd("call function[" + str(code.GetA()) + "] nparam:" + str(nparam) + ", nres:" + str(nres))
            state.PreCall(code.GetA(), nparam, nres)
            pc, func, p = self.enterCall()
            self.calls += 1
        elif oc == OP_RETURN:
            state.CloseUpval(state.GetBasei())
            state.Savedpc(pc)
            nres = state.GetTopi()
            b = code.GetB()
            if b != 0:
                nres = code.GetA() + b - 1
            ret_num = state.GetCurrentCallRetNum()
            state.PosCall(code.GetA())
            ret = ''
            for i in range(ret_num):
                ret += ' ' + state.GetStack(state.GetTopi() - i).toString()
            printd("return " + ret)
            self.calls -= 1
            if self.calls == 0:
                self.reset()
                return
            pc, func, p = self.enterCall()
        elif oc == OP_FORLOOP:
            step = state.GetStack(code.GetA() + 2).GetValue()
            idx = state.GetStack(code.GetA()).GetValue() + step
            n = state.GetStack(code.GetA() + 1).GetValue()
            printd("for i=%d, %d, %d do" % (idx, n, step))
            if (step <= 0 and idx >= n) or (step > 0 and idx <= n):
                pc += code.GetsBx()
                printd("pc->" + str(pc))
                state.SetStack(code.GetA(), toValue(idx))
                state.SetStack(code.GetA() + 3, toValue(idx))
                printd("set [%d] %d" % (code.GetA(), idx))
                printd("set [%d] %d" % (code.GetA() + 3, idx))
        elif oc == OP_FORPREP:
            n1 = state.GetStack(code.GetA()).GetValue()
            n2 = state.GetStack(code.GetA() + 2).GetValue()
            state.SetStack(code.GetA(), toValue(n1 - n2))
            printd("set [%d] %d" % (code.GetA(), n1 - n2))
            pc += code.GetsBx()
            printd("pc->" + str(pc))
        elif oc == OP_JMP:
            pc += code.GetsBx()
            printd("pc->" + str(pc))
        elif oc == OP_EQ:
            rb = rkb(code, state, p)
            rc = rkc(code, state, p)
            b = (code.GetA() != 0)
            if EqualV(rb, rc) == b:
                pc += code.GetsBx()
                print("pc->" + str(pc))
            pc += 1
        elif oc == OP_LT:
            rb = rkb(code, state, p)
            rc = rkc(code, state, p)
            b = (code.GetA() != 0)
            printd("if %s < %s then" % (rb.toString(), rc.toString()))
            if LessThenV(rb, rc) == b:
                pc += code.GetsBx()
                printd("pc->" + str(pc))
            pc += 1
        elif oc == OP_LE:
            rb = rkb(code, state, p)
            rc = rkc(code, state, p)
            b = (code.GetA() != 0)
            if LessEqualV(rb, rc) == b:
                pc += code.GetsBx()
                printd("pc->" + str(pc))
            pc += 1
        elif oc == OP_TEST:
            v = state.GetStack(code.GetA())
            b = 0
            if v.IsNil() or (v.IsBoolean() and not v.GetValue()):
                b = 1
            if b == code.GetC():
                pc += code.GetsBx()
                printd("pc->" + str(pc))
            pc += 1
        elif oc == OP_TESTSET:
            v = state.GetStack(code.GetB())
            b = 0
            if v.IsNil() or (v.IsBoolean() and not v.GetValue()):
                b = 1
            if b == code.GetC():
                state.CopyStack(code.GetB(), code.GetC())
                pc += code.GetsBx()
                printd("pc->" + str(pc))
            pc += 1
        else:
            printd("not process the op code:" + str(oc))
        state.ShowStack()
        self.pc = pc
        return code.toString()
