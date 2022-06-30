from flask import Flask
from undump import *
from lstate import *
from lvm import *

app = Flask(__name__)
ud = LuaUndump()
p = ud.undump("test.luac")
lua = None
vm = None
finish = False

def stackToString(stacks, code):
    global finish
    p = []
    for i, stk in enumerate(stacks):
        v = '{"i":%d, "type":"%s", "value":"%s"}' % (i + 1, TYPENAME[stk.GetType()], stk.toString())
        p.append(v)
    s = '{"stacks":[%s], "finish":"%s", "code":"%s"}' % (','.join(p), finish, code)
    return s

@app.route("/Start")
def start():
    global lua, vm, finish
    lua = LuaState()
    lua.LoadProto(p)
    lua.PreCall(0, 0, 0)
    vm = LuaVm(lua)
    finish = False
    stacks = lua.GetAllStack()
    return stackToString(stacks, "")

@app.route("/nextStep")
def nextStep():
    global finish
    code = ''
    if not finish:
        code = vm.executeOnce()
        if vm.getCalls() == 0:
            finish = True
    stacks = lua.GetAllStack()
    return stackToString(stacks, code)

def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

if __name__ == '__main__':
    app.after_request(after_request)
    app.run(host='0.0.0.0')