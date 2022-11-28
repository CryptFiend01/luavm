LUA_TNIL = 0
LUA_TBOOLEAN = 1
LUA_TLIGHTUSERDATA = 2
LUA_TNUMBER = 3
LUA_TSTRING = 4
LUA_TTABLE = 5
LUA_TFUNCTION = 6
LUA_TUSERDATA = 7
LUA_TTHREAD = 8

LUA_TPROTO = 9
LUA_TUPVAL = 10

TYPENAME = [
    "TNIL",
    "TBOOLEAN",
    "TLIGHTUSERDATA",
    "TNUMBER",
    "TSTRING",
    "TTABLE",
    "TFUNCTION",
    "TUSERDATA",
    "TTHREAD",
    "TPROTO",
    "TUPVAL"
]

LUA_MINSTACK = 20


OP_MOVE = 0         ## MOVE A B; -- R(A) := R(B)
OP_LOADK = 1        ## LOADK A Bx; -- R(A) := Kst(Bx)
OP_LOADBOOL = 2     ## LOADBOOL A B C; -- R(A) := (Bool)B; if (C) pc++
OP_LOADNIL = 3      ## LOADNIL A B; -- R(A), R(A+1), ..., R(B) := nil
OP_GETUPVAL = 4     ## GETUPVAL A B; -- R(A) := UpValue[B]
OP_GETGLOBAL = 5    ## GETGLOBAL A Bx; -- R(A) := Gbl[Kst(Bx)]
OP_GETTABLE = 6     ## GETTABLE A B C; -- R(A) := R(B)[RK(C)]
OP_SETGLOBAL = 7    ## SETGLOBAL A Bx; -- Gbl[Kst(Bx)] := R(A)
OP_SETUPVAL = 8     ## SETUPVAL A B; -- UpValue[B] := R(A)
OP_SETTABLE = 9     ## SETTABLE A B C; -- R(A)[RK(B)] := RK(C)
OP_NEWTABLE = 10    ## NEWTABLE A B C; -- R(A) := {}(size := B, C)
OP_SELF = 11        ## SELF A B C; -- R(A+1) := R(B); R(A) := R(B)[RK(C)]
OP_ADD = 12         ## ADD A B C; -- R(A) := R(B) + R(C)
OP_SUB = 13         ## SUB A B C; -- R(A) := R(B) - R(C)
OP_MUL = 14         ## MUL A B C; -- R(A) := R(B) * R(C)
OP_DIV = 15         ## DIV A B C; -- R(A) := R(B) * R(C)
OP_MOD = 16         ## MOD A B C; -- R(A) := R(B) % R(C)
OP_POW = 17         ## POW A B C; -- R(A) := pow(R(B), R(C))
OP_UMN = 18         ## UNM A B; -- R(A) := -R(B)
OP_NOT = 19         ## NOT A B; -- R(A) := not R(B)
OP_LEN = 20         ## LEN A B; -- R(A) := len(R(B))

OP_CONCAT = 21      ## CONCAT A B C; -- R(A) := R(B)..R(B+1).. ... ..R(C)

OP_JMP = 22         ## JMP sBx; -- pc += sBx
OP_EQ = 23          ## EQ A B C; -- if (RK(B) == RK(C)) ~= A) pc++
OP_LT = 24          ## LT A B C; -- if (RK(B) < RK(C)) ~= A) pc++
OP_LE = 25          ## LE A B C; -- if (RK(B) <= RK(C)) ~= A) pc++

OP_TEST = 26        ## TEST A C; -- if not (R(A) == C) pc++
OP_TESTSET = 27     ## TESTSET A B C; -- if (R(B) == C) R(A) := R(B) else pc++
OP_CALL = 28        ## CALL A B C; -- R(A), R(A+1), ..., R(A+C-2) := R(A)(R(A+1), R(A+2), ..., R(A+B-1))

OP_RETURN = 30      ## RETURN A B; return R(A), R(A+1), ..., R(A+B-2)
OP_FORLOOP = 31     ## FORLOOP A sBx; R(A) += R(A+2); if R(A) <= R(A+1) { pc += sBx; R(A+3) = R(A); }
OP_FORPREP = 32     ## FORPREP A sBx; R(A) -= R(A+2); pc += sBx;
OP_TFORLOOP = 33    ## TFORLOOP A C; R(A+3), R(A+4), ..., R(A+2+C) := R(A)(R(A+1), R(A+2))

OP_SETLIST = 34     ## SETLIST A B C; R(A)[(C-1)*FPF+i] := R(A+i), 1 <= i <= B

OP_CLOSURE = 36     ## CLOSURE A Bx; R(A) := closure(KPROTO[Bx], R(A), ..., R(A+n))

OP_VARARG = 37      ## VARARG A B; -- R(A), R(A+1), ..., R(A+B-1) = vararg

OPNAME = [
    'MOVE',
    'LOADK',
    'LOADBOOL',
    'LOADNIL',
    'GETUPVAL',
    'GETGLOBAL',
    'GETTABLE',
    'SETGLOBAL',
    'SETUPVAL',
    'SETTABLE',
    'NEWTABLE',
    'SELF',
    'ADD',
    'SUB',
    'MUL',
    'DIV',
    'MOD',
    'POW',
    'UNM',
    'NOT',
    'LEN',
    'CONCAT',
    'JMP',
    'EQ',
    'LT',
    'LE',
    'TEST',
    'TESTSET',
    'CALL',
    'TAILCALL',
    'RETURN',
    'FORLOOP',
    'FORPREP',
    'TFORLOOP',
    'SETLIST',
    'CLOSE',
    'CLOSURE',
    'VARARG',
]

FPF = 50 ## LFIELDS_PER_FLUSH number of list

def isnumber(n):
    return isinstance(n, int) or isinstance(n, float)

TK_NONE = 'TK_NONE'
TK_EQ = 'TK_EQ'
TK_COMMENT = 'TK_COMMENT'
TK_NUMBER = 'TK_NUMBER'
TK_STRING = 'TK_STRING'
TK_NAME = 'TK_NAME'
TK_NE = 'TK_NE'
TK_LE = 'TK_LE'
TK_GE = 'TK_GE'
TK_CONCAT = 'TK_CONCAT'

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

NO_JUMP = -1

NO_REG = (1 << SIZE_A) - 1