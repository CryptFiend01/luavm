from undump import *
from lstate import *
from lvm import *

if __name__ == '__main__':
    ud = LuaUndump()
    p = ud.undump("test.luac")
    #p.ShowCodes()
    #p.ShowConst()
    lua = LuaState()
    #lua.setPrint(True)
    lua.LoadProto(p)
    lua.PreCall(0, 0, 0)
    vm = LuaVm(lua)
    vm.execute()