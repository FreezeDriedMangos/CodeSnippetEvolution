import const
from const import *
import random

#
# Non-modifying utility functions
#
def findDump(simData, executorAddress):
    addr = executorAddress+1
    
    while addr < NUM_MEMORY_BLOCKS_IN_SOUP:
        block = readBlock(simData, addr)
        if block["header"]["name"] == "dump register":
            return addr
        addr += 1
        
    return -1


def findRegister(simData, executorAddress, regNum):
    regCount = -1
    addr = executorAddress
    
    while addr < NUM_MEMORY_BLOCKS_IN_SOUP:
        block = readBlock(simData, addr)
        if block is None:
            return -1
        
        if block["header"]["type"] == "register":
            regCount += 1
        
        if regCount == regNum:
            return addr
        addr += 1
        
    return -1


def readBlock(simData, blockIndex):
    if type(blockIndex) != int:
        return None
    if blockIndex < 0 or blockIndex >= NUM_MEMORY_BLOCKS_IN_SOUP:
        return None
    return simData.blocks[blockIndex]


def readRegister(simData, executorAddress, regNum):
    regAddress = findRegister(simData, executorAddress, regNum)
    return readBlock(simData, regAddress)
    

def decodeArgs(simData, address, count):
    queue = [0,1,2,3,4,5,6,7,8,9]
    arglist = []
    
    # any keys immediately after an instruction are ignored while decoding args
    start = 1
    block = readBlock(simData, address + start)
    while block != None and block['header']['type'] == "instruction" and block["body"]["type"] == "key":
        start += 1
        block = readBlock(simData, address + start)
        
    
    # the acceptMemArgs variable is used to make sure that only consecutive arguments are considered
    # ie: 
    # +235    here, all arguments are counted
    # +3u56   here, only the 3 is counted
    # +x863   here, no arguments are counted
    # without the acceptMemArgs variable, in all three examples, all 3 arguments would be counted
    acceptMemArgs = True
    for i in range(start, count+start):
        if acceptMemArgs:
            nextMemArg = readBlock(simData, address + i)
            
            if nextMemArg is None:
                # we've hit the end of the soup
                acceptMemArgs = False
                continue
            
            if nextMemArg["header"]["type"] == "instruction" and nextMemArg["body"]["code"][0:3] == "ARG":
                arg = int(nextMemArg["body"]["code"][3])
                arglist.append(arg)
                if arg in queue:
                    queue.remove(arg)
            else:
                acceptMemArgs = False
                arglist.append(queue.pop(0))
        else:
            arglist.append(queue.pop(0))
            
    return arglist

     
#
# Modifying utility functions
#
def registerWriteIgnoreDumpMechanics(simData, registerAddress, val):
    simData.setBlockBody(val, registerAddress)
    return 


def registerWrite(simData, executorAddress, registerAddress, val):
    assert(type(executorAddress) == int)
    assert(type(registerAddress) == int)
    assert(type(val) == int or type(val) == type(None))
    
    block = readBlock(simData, registerAddress)
    try:
        bbt = type(block["body"])
        assert(bbt == int or bbt == type(None))
    except:
        print("executor at ", executorAddress, " attempted to registerwrite to non-register:")
        print(block)
        raise
        
    
    if val == None:
        val = readBlock(simData, registerAddress)["body"]
        
        if val == None:
            return True
        
        # if the register wasn't already holding null
        addToDump(simData, executorAddress, abs(val))
        simData.setBlock(simData.opcodes.spawnNullRegister(), registerAddress)
        return True
    
    if REGISTER_WRITE_MUTATION_PROBABILITY > 0:
        if random.random() < REGISTER_WRITE_MUTATION_PROBABILITY:
            val += random.choice(range(*REGISTER_WRITE_MUTATION_RANGE))
            simData.logMutation(registerAddress, soft=True)
        
    # take the neccessary difference from the dump register
    initialize = False
    oldVal = readBlock(simData, registerAddress)["body"]
    if oldVal == None:
        oldVal = 0
        simData.setBlock(simData.opcodes.spawnRegister(), registerAddress)
        
    diff = abs(val) - abs(oldVal)
    success = takeFromDump(simData, executorAddress, diff)
    
    if not success:
        return False
    
    # the actual writing
    simData.setBlockBody(val, registerAddress)
        
    return True    


# returns False if there was an error
def takeFromDump(simData, executorAddress, val):
    if val == None:
        return True
    
    dumpAddr = findDump(simData, executorAddress)
    
    if dumpAddr == -1:
        return False
    
    dump = readBlock(simData, dumpAddr)
    
    if val > dump["body"]:
        return False
        
    newVal = dump["body"] - val
    simData.setBlockBody(newVal, dumpAddr)
    
    return True


def addToDump(simData, executorAddress, val):
    return takeFromDump(simData, executorAddress, -val)
    

def stackPush(simData, executorAddress, stackAddress, val):
    addr = stackAddress+1
    block = readBlock(simData, addr)
    
    while block != None and block["header"]["type"] == "register":
        if block["name"] == "register with a null value":
            simData.setBlock(simData.opcodes.spawnRegister(), addr)
            return registerWrite(simData, addr, val)
        addr += 1
        block = readBlock(simData, addr)
    return 'fail safe'
     
     
def stackPop(simData, executorAddress, stackAddress, registerAddress):
    addr = stackAddress+1
    block = readBlock(simData, addr)
    
    while block != None and block["header"]["type"] == "register":
        if block["name"] == "register with a null value":
            break
        addr += 1
        block = readBlock(simData, addr)
    
    addr -= 1
    block = readBlock(simData, addr) 

    if block == None or block["header"]["name"] != "register":    
        return 'fail safe'
        
    val = block["body"]
    registerWrite(simData, executorAddress, addr, None) # always successful
    return registerWrite(simData, executorAddress, registerAddress, val)
        

def killExecutor(simData, executorAddress):
    block = readBlock(simData, executorAddress)
    if block["header"]["type"] != "executor":
        print("Attempted to hibernate non-executor ", block["header"]["symbol"], " at ", executorAddress)
        return
    registerWrite(simData, executorAddress, executorAddress, None)
    simData.setBlock(simData.opcodes.spawnDormantExecutor(), executorAddress)
    

def awakenExecutor(simData, executorAddress):
    block = readBlock(simData, executorAddress)
    if block["header"]["type"] != "executor":
        print("Attempted to awaken non-executor ", block["header"]["symbol"], " at ", executorAddress)
        return
    simData.setBlock(simData.opcodes.spawnAwakeExecutor(), executorAddress)
    simData.setBlockBody(executorAddress, executorAddress)
    

def swapMemoryBlocks(simData, addr1, addr2):
    if addr1 < 0 or addr1 >= NUM_MEMORY_BLOCKS_IN_SOUP:
        return False
    if addr2 < 0 or addr2 >= NUM_MEMORY_BLOCKS_IN_SOUP:
        return False
    
    block1 = simData.blocks[addr1]
    block2 = simData.blocks[addr2]
    
    simData.setBlock(block1, addr2)
    simData.setBlock(block2, addr1)
    
    return True
    
 
# 
# Other
#

def blocksEquivalent(block1, block2):
    if block1 == None or block2 == None:
        if block1 == None and block2 == None:
            return True
        else:
            return False
        
    if block1["header"]["type"] == "instruction" and block2["header"]["type"] == "instruction":
        if block1["header"]["symbol"] == block2["header"]["symbol"]:
            return True
        return False
        
    if block1["header"]["type"] == block2["header"]["type"]: # will match (live executor, dormant executor) and (register, register with null) pairs
        return True
    return False
   

# returns true if the key really == a key, false otherwise
def keyCheck(key):
    if not key["header"]["type"] == "instruction":
        return False
        
    return key["body"]["type"] == "key"
   

# returns true if the lock really == a lock, false otherwise
def lockCheck(lock):
    if not lock["header"]["type"] == "instruction":
        return False
        
    return lock["body"]["type"] == "lock"
   
   
def keyLockMatch(key, lock):
    if not keyCheck(key) or not lockCheck(lock):
        return False
        
    if key["body"]["code"][3] == lock["body"]["code"][3]:
        return True
        
    if key["body"]["code"] == "CLMk" and lock["body"]["code"] == "CLAM":
        return True
    
    if key["body"]["code"] == "STCk" and lock["body"]["code"] == "STAC":
        return True
    
    return False
    
    
def getClaimBoundaries(simData, executorAddress):    
    start = executorAddress
    block = readBlock(simData, start)
    
    while block != None and not (block["header"]["type"] == "instruction" and block["body"]["code"] == "CLAM"):
        start -= 1
        block = readBlock(simData, start)
    
    end = executorAddress
    block = readBlock(simData, end)
    
    while block != None and not (block["header"]["type"] == "instruction" and block["body"]["code"] == "CLAM"):
        end += 1
        block = readBlock(simData, end)
    
    return (start, end)
    
   
# WARNING: SLOW FUNCTION 
def getClaimData(simData, executorAddress):
    boundaries = getClaimBoundaries(simData, executorAddress)
    return getSymbolRange(simData, *boundaries)
    

# WARNING: SLOW FUNCTION   
def getSymbolRange(simData, start, stop): 
    if start < 0:
        start = 0
    if start > NUM_MEMORY_BLOCKS_IN_SOUP:
        start = NUM_MEMORY_BLOCKS_IN_SOUP
    if stop < 0:
        stop = 0
    if stop > NUM_MEMORY_BLOCKS_IN_SOUP:
        stop = NUM_MEMORY_BLOCKS_IN_SOUP
        

    boundaries = (start, stop)    
    blocks = [readBlock(simData, i) for i in range(boundaries[0], boundaries[1]+1)]
    blocks = [block for block in blocks if block is not None]
    
    symbolString = ''.join(e["header"]["symbol"] for e in blocks)
    registerValues = [block["body"] for block in blocks if block["header"]["type"] == "register"]
    dumpRegisterValues = [block["body"] for block in blocks if block["header"]["type"] == "dump register"]
    
    
    executors = [{
                "address": i+start, 
                "ip": blocks[i]["body"], 
                "next instruction": None, 
                "active": blocks[i]["header"]["name"] == "executor"
                } for i in range(len(blocks)) if blocks[i]["header"]["type"] == "executor"]
    
    for i in range(len(executors)):
        addr = executors[i]["address"] - start
        ins = None
        try:
            ins = readBlock(simData, blocks[addr]["body"])["header"]["symbol"]
        except:
            ins = "out of bounds"
        executors[i].update({"next instruction": ins})
    
    
    return {
        "range bounds": (boundaries[0], boundaries[1]+1, ),
        "boundaries": boundaries,
        "symbols": symbolString,
        "register values": registerValues,
        "dump register values": dumpRegisterValues,
        "executors": executors
        }
    
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
