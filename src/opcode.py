from instructionFunctions import *
import const
from const import *

class Opcodes:
    BLOCK_TYPES = [
        {
            "symbol":         '░', 
            "code":           "0000",
            "type":           "uninitialized", 
            "name":           "uninitialized block", 
            "execute?":       False, 
            "spawnable?":     False,
            "interpret body": lambda self, s : None, 
            "default body":   None,
        },
    
        {
            "symbol":         '#', 
            "code":           "REG#",
            "type":           "register", 
            "name":           "register", 
            "execute?":       False,
            "spawnable?":     True, 
            "interpret body": lambda self, s : s, 
            "default body":   0
        },
        {
            "symbol":         '_', 
            "code":           "REGn",
            "type":           "register", 
            "name":           "register with a null value", 
            "execute?":       False, 
            "spawnable?":     True, 
            "interpret body": lambda self, s : None, 
            "default body":   None
        },
    
        {
            "symbol":         '▯', 
            "code":           "DUMP",
            "type":           "dump register", 
            "name":           "dump register", 
            "execute?":       False,
            "spawnable?":     True,  
            "interpret body": lambda self, s : abs(s), 
            "default body":   99999
        },
        { # these should never exist in an actual simulation
            "symbol":         '█', 
            "code":           "DMPn",
            "type":           "dump register", 
            "name":           "dump register with a null value", 
            "execute?":       False, 
            "spawnable?":     False, 
            "interpret body": lambda self, s : None, 
            "default body":   None
        }, 
    
        {
            "symbol":         '◈', 
            "code":           "EXEC",
            "type":           "executor", 
            "name":           "executor", 
            "execute?":       False, 
            "spawnable?":     False, 
            "interpret body": lambda self, s : abs(s), 
            "default body":   None
        }, # the core, driving life force of an organism. This is what makes the organism alive (it reads and executes instructions, basically)
        {
            "symbol":         '◇', 
            "code":           "EXEn",
            "type":           "executor", 
            "name":           "dormant executor", 
            "execute?":       False, 
            "spawnable?":     True, 
            "interpret body": lambda self, s : None, 
            "default body":   None
        }, # a dormant executor. May be part of a dead organism. Can be reawakened if moved or otherwise interacted with
    
        {
            "symbol":         None, 
            "code":           None,
            "type":           "instruction", 
            "name":           "instruction block", 
            "execute?":       True, 
            "spawnable?":     True,  
            "interpret body": lambda self, s: s,
            "default body":   None
        }
    ]
    
    # when instructions are given arguments, they remove those arguments from a queue and pop from the queue to fill the remaining arguments
    # the unmodified queue is [0,1,2,3,4,5,6,7,8,9]
    # so the instructions +25 would correspond to ([r2] = [r5] + [r0])
    # and                 +00 would correspond to ([r0] = [r0] + [r1])
    FAULT_INSTRUCTION = {"code": "FALT", "symbol": '⚠', "type": "noop", "arg count": 0, "function": fault, "description": "Just faults. Used for failed interprets."}

    INSTRUCTIONS = [
        {"code": "NOOP", "symbol": ' ', "type": "noop", "arg count": 0, "function": noOp, "description": "No operation"},
        {"code": "ARG_", "symbolrange": '0123456789', "type": "arg", "arg count": 0, "function": noOp, "description": "No operation. Modifies registers to be used by previous instruction"},
        
        {"code": "JMPR", "symbol": '%', "type": "jump", "arg count": 1, "function": jumpR, "description": "Jump to the address in r0."},
            
        {"code": "JMPB", "symbol": '(', "type": "jump", "arg count": 0, "function": jumpB, "description": "Jump backwards to the first lock matching the following key"},
        {"code": "JMPF", "symbol": ')', "type": "jump", "arg count": 0, "function": jumpF, "description": "Jump forwards to the first lock matching the following key"},
        {"code": "ADRB", "symbol": '[', "type": "lookaround", "arg count": 1, "function": addressOfJumpB, "description": "Look backwards to the first lock matching the following key, store its address in r0"},
        {"code": "ADRF", "symbol": ']', "type": "lookaround", "arg count": 1, "function": addressOfJumpF, "description": "Look forwards to the first lock matching the following key, store its address in r0"},
        # consider removing these two
        {"code": "SERB", "symbol": '<', "type": "lookaround", "arg count": 3, "function": addressOfInstructionB, "description": "Starting from [r0], look backwards for the first instruction matching the instruction at [r1], store its address in r2"},
        {"code": "SERF", "symbol": '>', "type": "lookaround", "arg count": 3, "function": addressOfInstructionF, "description": "Starting from [r0], look forwards for the first instruction matching the instruction at [r1], store its address in r2"},
        
        {"code": "IFNZ", "symbol": '?', "type": "conditional", "arg count": 1, "function": skipIfZero, "description": "if [r0] is not 0, execute the following instruction, otherwise, skip to the next non-argument instruction"},
        {"code": "IFNN", "symbol": '‽', "type": "conditional", "arg count": 1, "function": skipIfNull, "description": "if [r0] is not null, execute the following instruction, otherwise, skip to the next non-argument instruction"},
        {"code": "IFDZ", "symbol": '¿', "type": "conditional", "arg count": 0, "function": skipIfDumpIsZero, "description": "if the instruction at the address in r0 is the same as the instruction at the address in r1 (or if they're both registers, dump registers, or executors), execute the next instruction, otherwise, skip to the next non-argument instruction"},
        {"code": "IFBE", "symbol": '⸘', "type": "conditional", "arg count": 2, "function": skipUnlessEquiv, "description": "if the instruction at the address in r0 is the same as the instruction at the address in r1 (or if they're both registers, dump registers, or executors), execute the next instruction, otherwise, skip to the next non-argument instruction"},
        {"code": "IFEQ", "symbol": '=', "type": "conditional", "arg count": 2, "function": skipUnlessEqual, "description": "if [r0] == [r1], execute the next instruction, otherwise, skip to the next non-argument instruction"},
        
        {"code": "ADDr", "symbol": '+', "type": "arithmetic", "arg count": 3, "function": add,      "description": "Add registers' contents ([r0] = [r1] + [r2])"},
        {"code": "SUBr", "symbol": '-', "type": "arithmetic", "arg count": 3, "function": subtract, "description": "Subtract registers' contents ([r0] = [r1] - [r2])"},
        {"code": "MULr", "symbol": '*', "type": "arithmetic", "arg count": 3, "function": multiply, "description": "Multiply registers' contents ([r0] = [r1] * [r2])"},
        {"code": "DIVr", "symbol": '÷', "type": "arithmetic", "arg count": 3, "function": divide,   "description": "Divide registers' contents ([r0] = [r1] ÷ [r2])"},
        
        {"code": "INCr", "symbol": '^', "type": "arithmetic", "arg count": 1, "function": increment, "description": "Increment register's contents ([r0]++)"},
        {"code": "DECr", "symbol": 'v', "type": "arithmetic", "arg count": 1, "function": decrement, "description": "Decrement register's contents ([r0]--)"},
        
        # deprecated as a part of the great debinarification
        # may be brought back in the future with new functions
        #{"code": "NOTr", "symbol": '!', "type": "bitwise", "arg count": 1, "function": bitwiseInverse,    "description": "Bitwise NOT register's contents ([r0] = ![r0])"},
        #{"code": "SHFL", "symbol": '«', "type": "bitwise", "arg count": 1, "function": bitwiseShiftLeft,  "description": "Bitwise left shift register's contents ([r0] = [r0] << 1)"},
        #{"code": "SHFR", "symbol": '»', "type": "bitwise", "arg count": 1, "function": bitwiseShiftRight, "description": "Bitwise right shift register's contents ([r0] = [r0] >> 1)"},

        #{"code": "ANDr", "symbol": '&', "type": "bitwise", "arg count": 3, "function": bitwiseAND, "description": "Bitwise AND register's contents ([r0] = [r1] & [r2])"},
        #{"code": "ORr-", "symbol": '|', "type": "bitwise", "arg count": 3, "function": bitwiseOR,  "description": "Bitwise OR register's contents ([r0] = [r1] | [r2])"},
        #{"code": "XORr", "symbol": '⊕', "type": "bitwise", "arg count": 3, "function": bitwiseXOR, "description": "Bitwise XOR register's contents ([r0] = [r1] ^ [r2])"},
        
        {"code": "ZERO", "symbol": 'z', "type": "set register", "arg count": 1, "function": setToZero, "description": "Set register contents to 0 ([r0] = 0)"},
        {"code": "UNIT", "symbol": 'u', "type": "set register", "arg count": 1, "function": setToOne,  "description": "Set register contents to 1 ([r0] = 1)"},
        {"code": "RAND", "symbol": 'r', "type": "set register", "arg count": 1, "function": setToRand, "description": "Sets [r0] to a random valid address."},
        {"code": "NULL", "symbol": 'n', "type": "set register", "arg count": 1, "function": setToNull, "description": "Sets [r0] to null."},
            
        {"code": "CPYr", "symbol": '"', "type": "misc register", "arg count": 2, "function": copy, "description": "Copy [r0] into r1"},
        {"code": "SWPr", "symbol": 'x', "type": "misc register", "arg count": 2, "function": swap, "description": "Swap [r0] into r1 and [r1] into r0"},
        
        {"code": "POPr", "symbol": '↑', "type": "stack", "arg count": 1, "function": pop,  "description": "Pop into r0 a value from the first stack found immediately after the first matching lock found after this executor"},
        {"code": "PSHr", "symbol": '↓', "type": "stack", "arg count": 1, "function": push, "description": "Push [r0] to the first stack found immediately after the first matching lock found after this executor"},
        # consider adding a 'stack lock' a special lock like the claim lock and the only valid lock that signifies a stack. symbol 'S'
        #{"code": "STAC", "symbol": 'S', "type": "lock", "arg count": 0, "function": noOp, "description": "A stack marker, used to mark the base of a stack. Also functions as lock."},
        #{"code": "STCk", "symbol": 's', "type": "key",  "arg count": 0, "function": noOp, "description": "A stack marker key, matches to a stack marker."},
        
        {"code": "CLAM", "symbol": 'T', "type": "lock", "arg count": 0, "function": noOp,       "description": "A claim marker, used to stake an executor's territory; the boundaries of an organism. Also functions as lock."},
        {"code": "CLMk", "symbol": 't', "type": "key",  "arg count": 0, "function": noOp,       "description": "A claim marker key, matches to a claim marker."},
        {"code": "MNTR", "symbol": '~', "type": "monitor", "arg count": 2, "function": monitor, "description": "Sets [r0] to the address most recently checked within this executor's claim boundaries, and [r1] to the address of the instruction that checked it. Both are set register to null if no checks have been recently made."},
        
        {"code": "ADRS", "symbol": '$', "type": "memwrite", "arg count": 2, "function": swapMemoryBlocks, "description": "Swap the memory block at [r0] with the block at [r1]"},
        # consider adding an "instruction to number" instruction that looks at an instruction at address [r0] and puts its numerical value in r1
        # also an instruction that adds the value of instruction at [r1] to the one at [r0], turning [r1] into a noop
        # also an instruction that takes half the value of @[r1] and adds it to @[r0]
        # this will allow creatures to have better tools for manipulating their environment
        
        {"code": "INIT", "symbol": ':', "type": "init", "arg count": 1, "function": initializeExecutor, "description": "Initializes the executor at the address contained in r0. (Sets it to non-dormant and set registers its instruction pointer to itself.)"},
        {"code": "DINT", "symbol": '.', "type": "deinit", "arg count": 1, "function": denitializeExecutor, "description": "Denitializes the executor at the address contained in r0. (Sets it to dormant.)"},
        
        {"code": "KEY_", "symbolrange": "abcdefghijklm", "type": "key", "arg count": 0, "function": noOp, "description": "A key used by some instructions to find a matching upper case lock"},
        {"code": "LOK_", "symbolrange": "ABCDEFGHIJKLM", "type": "lock", "arg count": 0, "function": noOp, "description": "A lock used by some instructions to match to a lower case key"} 
    ]

    _SYMBOL_DICTIONARY = {}

    def __init__(self):
        # unpack compressed instruction lists
        removeList = []
        insertList = []
        for i in range(len(self.INSTRUCTIONS)):
            instructionEntry = self.INSTRUCTIONS[i]
            
            if "symbolrange" in instructionEntry:
                #self.INSTRUCTIONS.pop(i)
                removeList.append(instructionEntry)
                
                for symbol in instructionEntry["symbolrange"]:
                    instruction = {
                        "code": instructionEntry["code"].replace('_', symbol.upper()), 
                        "symbol": symbol, 
                        "arg count": instructionEntry["arg count"], 
                        "function": instructionEntry["function"], 
                        "description": instructionEntry["description"],
                        "type": instructionEntry["type"]
                    }
                    # self.INSTRUCTIONS.insert(i, instruction)
                    insertList.append([i+len(insertList), instruction])

        for elem in insertList:
            self.INSTRUCTIONS.insert(elem[0], elem[1])

        for elem in removeList:
            self.INSTRUCTIONS.remove(elem)
            
        instructionHeader = self.BLOCK_TYPES[-1]
        self._SYMBOL_DICTIONARY.update({e["symbol"]: self._buildBlock(e, None) for e in self.BLOCK_TYPES if e["symbol"] is not None})
        self._SYMBOL_DICTIONARY.update({e["symbol"]: self._buildBlock(instructionHeader, e) for e in self.INSTRUCTIONS})
        


    def _buildBlock(self, header, body):
        return {"header":header, "body":body}


    def fetchBlock(self, symbol):
        proto = self._SYMBOL_DICTIONARY[symbol]
        
        header = proto["header"].copy()
        body = proto["body"]
        
        if body == None:
            body = proto["header"]["default body"]
        else:
            body = body.copy()
        
        if header["symbol"] == None:
           header["symbol"] = body["symbol"] 
        
        return {"header": header, "body": body}


    def spawnNullRegister(self):
        return self.fetchBlock("_")
    
    
    def spawnRegister(self):
        return self.fetchBlock("#")
    
    
    def spawnDormantExecutor(self):
        return self.fetchBlock("◇")
    
    
    def spawnAwakeExecutor(self):
        return self.fetchBlock("◈")
    
    
