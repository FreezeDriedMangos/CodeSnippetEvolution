from instructionFunctions import *
from utils import binaryToInt
from utils import intToBinaryUnsigned
import const

# this is important because once a genome is assembled, it can only be interpreted or dissasembled
# using the exact version it was assembled with
OPCODE_VER = 'v1.0'


# when instructions are given arguments, they remove those arguments from a queue and pop from the queue to fill the remaining arguments
# the unmodified queue is [0,1,2,3,4,5,6,7,8,9]
# so the instructions +25 would correspond to ([r2] = [r5] + [r0])
# and                 +00 would correspond to ([r0] = [r0] + [r1])

INSTRUCTIONS = [
    {"code": "NOOP", "symbol": ' ', "arg count": 0, "function": noOp, "description": "No operation"},
    {"code": "ARG_", "symbolrange": '0123456789', "arg count": 0, "function": noOp, "description": "No operation. Modifies registers to be used by previous instruction"},
    
    {"code": "JMPR", "symbol": '%', "arg count": 1, "function": jumpR, "description": "Jump to the address in r0."},
        
    {"code": "JMPB", "symbol": '(', "arg count": 0, "function": jumpB, "description": "Jump backwards to the first lock matching the following key"},
    {"code": "JMPF", "symbol": ')', "arg count": 0, "function": jumpF, "description": "Jump forwards to the first lock matching the following key"},
    {"code": "ADRB", "symbol": '[', "arg count": 1, "function": addressOfJumpB, "description": "Look backwards to the first lock matching the following key, store its address in r0"},
    {"code": "ADRF", "symbol": ']', "arg count": 1, "function": addressOfJumpF, "description": "Look forwards to the first lock matching the following key, store its address in r0"},
    
    {"code": "IFNZ", "symbol": '?', "arg count": 1, "function": skipIfZero, "description": "if [r0] is not 0, execute the following instruction, otherwise, skip to the next non-argument instruction"},
    {"code": "IFNN", "symbol": '‽', "arg count": 1, "function": skipIfNull, "description": "if [r0] is not null, execute the following instruction, otherwise, skip to the next non-argument instruction"},
    {"code": "IFDZ", "symbol": '¿', "arg count": 0, "function": skipIfDumpIsZero, "description": "if the instruction at the address in r0 is the same as the instruction at the address in r1 (or if they're both registers, dump registers, or executors), execute the next instruction, otherwise, skip to the next non-argument instruction"},
    {"code": "IFBE", "symbol": '⸘', "arg count": 2, "function": skipUnlessEquiv, "description": "if the instruction at the address in r0 is the same as the instruction at the address in r1 (or if they're both registers, dump registers, or executors), execute the next instruction, otherwise, skip to the next non-argument instruction"},
    {"code": "IFEQ", "symbol": '=', "arg count": 2, "function": skipUnlessEqual, "description": "if [r0] == [r1], execute the next instruction, otherwise, skip to the next non-argument instruction"},
     
    {"code": "ADDr", "symbol": '+', "arg count": 3, "function": add,      "description": "Add registers' contents ([r0] = [r1] + [r2])"},
    {"code": "SUBr", "symbol": '-', "arg count": 3, "function": subtract, "description": "Subtract registers' contents ([r0] = [r1] - [r2])"},
    {"code": "MULr", "symbol": '*', "arg count": 3, "function": multiply, "description": "Multiply registers' contents ([r0] = [r1] * [r2])"},
    {"code": "DIVr", "symbol": '÷', "arg count": 3, "function": divide,   "description": "Divide registers' contents ([r0] = [r1] ÷ [r2])"},
    
    {"code": "INCr", "symbol": '^', "arg count": 1, "function": increment, "description": "Increment register's contents ([r0]++)"},
    {"code": "DECr", "symbol": 'v', "arg count": 1, "function": decrement, "description": "Decrement register's contents ([r0]--)"},
    
    {"code": "NOTr", "symbol": '!', "arg count": 1, "function": bitwiseInverse,    "description": "Bitwise NOT register's contents ([r0] = ![r0])"},
    {"code": "SHFL", "symbol": '«', "arg count": 1, "function": bitwiseShiftLeft,  "description": "Bitwise left shift register's contents ([r0] = [r0] << 1)"},
    {"code": "SHFR", "symbol": '»', "arg count": 1, "function": bitwiseShiftRight, "description": "Bitwise right shift register's contents ([r0] = [r0] >> 1)"},

    {"code": "ANDr", "symbol": '&', "arg count": 3, "function": bitwiseAND, "description": "Bitwise AND register's contents ([r0] = [r1] & [r2])"},
    {"code": "ORr-", "symbol": '|', "arg count": 3, "function": bitwiseOR,  "description": "Bitwise OR register's contents ([r0] = [r1] | [r2])"},
    {"code": "XORr", "symbol": '⊕', "arg count": 3, "function": bitwiseXOR, "description": "Bitwise XOR register's contents ([r0] = [r1] ^ [r2])"},
    
    {"code": "ZERO", "symbol": 'z', "arg count": 1, "function": setToZero, "description": "Set register contents to 0 ([r0] = 0)"},
    {"code": "UNIT", "symbol": 'u', "arg count": 1, "function": setToOne,  "description": "Set register contents to 1 ([r0] = 1)"},
    {"code": "RAND", "symbol": 'r', "arg count": 1, "function": setToRand, "description": "Sets [r0] to a random valid address."},
    {"code": "NULL", "symbol": 'n', "arg count": 1, "function": setToNull, "description": "Sets [r0] to null."},
        
    {"code": "CPYr", "symbol": '"', "arg count": 2, "function": copy, "description": "Copy [r0] into r1"},
    {"code": "SWPr", "symbol": 'x', "arg count": 2, "function": swap, "description": "Swap [r0] into r1 and [r1] into r0"},
    
    {"code": "POPr", "symbol": '↑', "arg count": 1, "function": pop,  "description": "Pop into r0 a value from the first stack found immediately after the first matching lock found after this executor"},
    {"code": "PSHr", "symbol": '↓', "arg count": 1, "function": push, "description": "Push [r0] to the first stack found immediately after the first matching lock found after this executor"},
    # consider adding a 'stack lock' a special lock like the claim lock and the only valid lock that signifies a stack. symbol 'S'
    
    {"code": "CLAM", "symbol": 'T', "arg count": 0, "function": noOp,             "description": "A claim marker, used to stake an executor's territory; the boundaries of an organism. Also functions as lock."},
    {"code": "CLMk", "symbol": 't', "arg count": 0, "function": noOp,             "description": "A claim marker key, matches to a claim marker."},
    {"code": "MNTR", "symbol": '~', "arg count": 2, "function": monitor,          "description": "Sets [r0] to the address most recently checked within this executor's claim boundaries, and [r1] to the address of the instruction that checked it. Both are set to null if no checks have been recently made."},
    
    {"code": "ADRS", "symbol": '$', "arg count": 2, "function": swapMemoryBlocks, "description": "Swap the memory block at [r0] with the block at [r1]"},
    
    {"code": "INIT", "symbol": ':', "arg count": 1, "function": initializeExecutor, "description": "Initializes the executor at the address contained in r0. (Sets it to non-dormant and sets its instruction pointer to itself.)"},
    {"code": "DINT", "symbol": '.', "arg count": 1, "function": denitializeExecutor, "description": "Denitializes the executor at the address contained in r0. (Sets it to dormant.)"},
    
    {"code": "KEY_", "symbolrange": "abcdefghijklm", "arg count": 0, "function": noOp, "description": "A key used by some instructions to find a matching upper case lock"},
    {"code": "LOK_", "symbolrange": "ABCDEFGHIJKLM", "arg count": 0, "function": noOp, "description": "A lock used by some instructions to match to a lower case key"}
    
]

# unpack compressed instruction lists
for i in range(len(INSTRUCTIONS)):
    instructionEntry = INSTRUCTIONS[i]
    
    if instructionEntry["symbol list"] is not None:
        INSRUCTIONS.removeIndex(i)
        
        for symbol in instructionEntry["symbol list"]:
            instruction = {
                "name": instructionEntry["name"].replaceAll('_', symbol.upper()), 
                "symbol": symbol, 
                "arg count": instructionEntry["arg count"], 
                "function": instructionEntry["function"], 
                "description": instructionEntry["description"]
            }
            INSTRUCTIONS.add(i, instruction)


# the simulation's simulated RAM is segmented into blocks. Each block is made of a header and body
#
#   _ _ _ | _ _ _ _ _ _
#  header    body
#
# the header consists only of the flags listed below
# the meaning of each flag combination is listed below
#
# what the body is used for depends on the flags
# in an instruction block, the body is used to identify which instruction it represents
# in an executor block, the body is used to store the value of the instruction pointer
# in a register, the body is used to store the register's value

FLAG_NAMES = ["special", "isRegister", "isNonNull"]
    
FLAG_CODES = {
    '000': {
        "symbol":         '░', 
        "code":           "0000",
        "type":           "uninitialized", 
        "name":           "uninitialized block", 
        "execute?":       False, 
        "interpret body": lambda s : None, 
        "default body":   '0'*BODY_LEN
        },
    
    '011': {
        "symbol":         '#', 
        "code":           "REG#",
        "type":           "register", 
        "name":           "register", 
        "execute?":       False, 
        "interpret body": lambda s : binaryToInt(s), 
        "default body":   '0'*BODY_LEN
        },
    '010': {
        "symbol":         '_', 
        "code":           "REGn",
        "type":           "register", 
        "name":           "register with a null value", 
        "execute?":       False, 
        "interpret body": lambda s : None, 
        "default body":   '0'*BODY_LEN
        },
    
    '111': {
        "symbol":         '▯', 
        "code":           "DUMP",
        "type":           "dump register", 
        "name":           "dump register", 
        "execute?":       False, 
        "interpret body": lambda s : binaryToInt(s, unsigned=True), 
        "default body":   '1'*BODY_LEN
        },
    '110': { # these should never exist in an actual simulation
        "symbol":         '█', 
        "code":           "DMPn",
        "type":           "dump register", 
        "name":           "dump register with a null value", 
        "execute?":       False, 
        "interpret body": lambda s : None, 
        "default body":   '0'*BODY_LEN
        }, 
    
    '101': {
        "symbol":         '◈', 
        "code":           "EXEC",
        "type":           "executor", 
        "name":           "executor", 
        "execute?":       False, 
        "interpret body": lambda s : binaryToInt(s, unsigned=True), 
        "default body":   '0'*BODY_LEN
        }, # the core, driving life force of an organism. This is what makes the organism alive (it reads and executes instructions, basically)
    '100': {
        "symbol":         '◇', 
        "code":           "EXEn",
        "type":           "executor", 
        "name":           "dormant executor", 
        "execute?":       False, 
        "interpret body": lambda s : None, 
        "default body":   '0'*BODY_LEN
        }, # a dormant executor. May be part of a dead organism. Can be reawakened if moved or otherwise interacted with
    
    '001': {
        "symbol":         None, 
        "code":           None,
        "type":           "instruction", 
        "name":           "instruction block", 
        "execute?":       True,  
        "interpret body": lambda s : INSTRUCTIONS[binaryToInt(s, unsigned=True)],
        "default body":   None
        },
}

SPAWN_LIST = list(
    '011' + '0' * BODY_LEN, # an empty register - may be initialized with a random value later
    '100' + '0' * BODY_LEN, # a dormant executor 
    '111' + '1' * (BODY_LEN)  # a dump register with the maximum value (note: dump registers are unsigned)
).append(list('001' + intToBinaryUnsigned(i, BODY_LEN) for i in range(len(INSTRUCTIONS)))) # all instructions


