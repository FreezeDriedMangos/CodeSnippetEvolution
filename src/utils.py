import const
from const import *
import random

def binaryToInt(string, unsigned=False):
    signedPlace = len(string)-1
    if unsigned:
        signedPlace=-1
        
    placeValue = 1
    value = 0
    i = 0
    
    for bit in string[::-1]:
        if i == signedPlace:
            placeValue *= -1
            
        value += int(bit) * placeValue
        placeValue *= 2
        i += 1
        
    return value
        
    
def intToBinary(val, length, unsigned=False):
    assert(type(val) == int)
    assert((val < 0 and not unsigned) or val >= 0) # can't have an unsigned negative number
    
    if not unsigned and val > (2**(length-1) - 1):
        val = (2**(length-1) - 1)
    
    if val < 0 and not unsigned:
        val -= -2**(length-1)
        return '1' + intToBinaryUnsigned(val, length-1)
    return intToBinaryUnsigned(val, length) 
        
    
def intToBinaryUnsigned(val, length):    
    if val > (2**length - 1):
        val = (2**length - 1)
    
    placeValue = 2 ** (length-1)
    retval = ""
    
    for i in range(length):
        if val >= placeValue:
            val -= placeValue
            retval += "1"
        else:
            retval += "0"
            
        placeValue /= 2
    return retval
    
    
def bitwiseInverse(intVal, bitLen, unsigned=False):
    assert(type(intVal) == int)    
    binary = intToBinary(intVal, bitLen, unsigned=unsigned)
    binary = ''.join('1' if bit == '0' else '0' for bit in binary)
    
    return binaryToInt(binary, unsigned=unsigned)
    
    
def bitwiseShiftLeft(intVal, bitLen, unsigned=False):
    assert(type(intVal) == int)    
    binary = intToBinary(intVal, bitLen, unsigned=unsigned)
    binary = binary[1:] + binary[-1]
    
    return binaryToInt(binary, unsigned=unsigned)
    
    
def bitwiseShiftRight(intVal, bitLen, unsigned=False):
    assert(type(intVal) == int)    
    binary = intToBinary(intVal, bitLen, unsigned=unsigned)
    binary = binary[0] + binary[0:-1]
    
    return binaryToInt(binary, unsigned=unsigned)
    
  
def bitwiseAND(intVal1, intVal2, bitLen, unsigned=False):
    assert(type(intVal1) == int)   
    assert(type(intVal2) == int)    
    
    binary1 = [bit == '1' for bit in intToBinary(intVal1, bitLen, unsigned=unsigned)]
    binary2 = [bit == '1' for bit in intToBinary(intVal2, bitLen, unsigned=unsigned)]
    
    binary = ''.join('1' if (a and b) else '0' for a, b in zip(binary1, binary2))
    
    return binaryToInt(binary, unsigned=unsigned)
    
   
def bitwiseOR(intVal1, intVal2, bitLen, unsigned=False):
    assert(type(intVal1) == int)   
    assert(type(intVal2) == int)    
    
    binary1 = [bit == '1' for bit in intToBinary(intVal1, bitLen, unsigned=unsigned)]
    binary2 = [bit == '1' for bit in intToBinary(intVal2, bitLen, unsigned=unsigned)]
    
    binary = ''.join('1' if (a or b) else '0' for a, b in zip(binary1, binary2))
    
    return binaryToInt(binary, unsigned=unsigned)
    
     
def bitwiseXOR(intVal1, intVal2, bitLen, unsigned=False):
    assert(type(intVal1) == int)   
    assert(type(intVal2) == int)    
    
    binary1 = [bit == '1' for bit in intToBinary(intVal1, bitLen, unsigned=unsigned)]
    binary2 = [bit == '1' for bit in intToBinary(intVal2, bitLen, unsigned=unsigned)]
    
    binary = ''.join('1' if (a != b) else '0' for a, b in zip(binary1, binary2))
    
    return binaryToInt(binary, unsigned=unsigned)
    
         
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
    while block['header']['type'] == "instruction" and block["body"]["type"] == "key":
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
            if nextMemArg["header"]["type"] == "instruction" and nextMemArg["body"]["code"][0:3] == "ARG":
                arg = int(nextMemArg["body"]["code"][3])
                arglist.append(arg)
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
def registerWriteIgnoreDumpMechanics(simData, registerAddress, val, unsigned=False):
    binary = intToBinary(val, BODY_LEN, unsigned=unsigned)
    #simData.soup.overwrite(binary, MEM_BLOCK_LEN*registerAddress+HEADER_LEN)
    
    #simData.logBlockUpdate(registerAddress, wholeBlock=False)
    simData.setBlockBody(binary, registerAddress)
    return 


def registerWrite(simData, executorAddress, registerAddress, val, unsigned=False):
    if val == None:
        val = readBlock(simData, registerAddress)["body"]
        
        if val == None:
            return
        # if the register wasn't already none
        addToDump(simData, executorAddress, abs(val))
        
        #binary = "0b" + '0'*BODY_LEN 
        #simData.soup.overwrite(binary, MEM_BLOCK_LEN*registerAddress+HEADER_LEN)
        #simData.soup.overwrite("0b"+'010', MEM_BLOCK_LEN*registerAddress)
        
        #simData.logBlockUpdate(registerAddress, wholeBlock=True)
        simData.setBlock('010'+'0'*BODY_LEN, registerAddress)
        return
    
    
    if random.random() < REGISTER_WRITE_MUTATION_PROBABILITY:
        val += random.choice(range(*REGISTER_WRITE_MUTATION_RANGE))
        simData.logMutation(registerAddress, soft=True)
        
    # take the neccessary difference from the dump register
    initialize = False
    oldVal = readBlock(simData, registerAddress)["body"]
    if oldVal == None:
        oldVal = 0
        initialize = True
        #registerInitialize(simData, registerAddress)
        #simData.logBlockUpdate(registerAddress, wholeBlock=True)
    
    #simData.logBlockUpdate(registerAddress, wholeBlock=False)
    
    diff = abs(val) - abs(oldVal)
    success = takeFromDump(simData, executorAddress, diff)
    
    if not success:
        return False
    
    # the actual writing
    binary = intToBinary(val, BODY_LEN, unsigned=unsigned)
    #simData.soup.overwrite(binary, MEM_BLOCK_LEN*registerAddress+HEADER_LEN)
       
    #print(oldVal, " -> ", readBlock(simData, registerAddress)["body"])   
        
    if initialize:
        simData.setBlock('011'+binary, registerAddress)
    else:
        simData.setBlockBody(binary, registerAddress)
        
    return True    


#def registerInitialize(simData, registerAddress):
    #simData.logBlockUpdate(registerAddress, wholeBlock=True)
    
    #block = readBlock(simData, registerAddress)
    #assert(block["header"]["name"] == "register with a null value")
    
    #simData.soup.overwrite("0b"+'011' + ('0'*BODY_LEN), MEM_BLOCK_LEN*registerAddress)


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
        
    #simData.logBlockUpdate(dumpAddr, wholeBlock=False)
    
    binary = intToBinary(dump["body"] - val, BODY_LEN, unsigned=True)
    #simData.soup.overwrite(binary, MEM_BLOCK_LEN*dumpAddr+HEADER_LEN)
    simData.setBlockBody(binary, dumpAddr)
    
    return True


def addToDump(simData, executorAddress, val):
    return takeFromDump(simData, executorAddress, -val)
    

def stackPush(simData, executorAddress, stackAddress, val):
    addr = stackAddress+1
    block = readBlock(simData, addr)
    
    while block != None and block["header"]["type"] == "register":
        if block["name"] == "register with a null value":
            registerInitialize(simData, addr)
            return registerWrite(simData, executorAddress, val)
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
    binary = '100'
    #simData.soup.overwrite(binary, MEM_BLOCK_LEN*executorAddress)
        
    #simData.logBlockUpdate(executorAddress, wholeBlock=True)
    simData.setBlockHeader(binary, executorAddress)
    

def awakenExecutor(simData, executorAddress):
    # overwrite the header information (making this an active executor) and overwrite the body so the ip points to itself
    binary = '101' + intToBinary(executorAddress, BODY_LEN, unsigned=True)
    #simData.soup.overwrite(binary, MEM_BLOCK_LEN*executorAddress)
 
    #simData.logBlockUpdate(executorAddress, wholeBlock=True)
    simData.setBlock(binary, executorAddress)
    

def swapMemoryBlocks(simData, addr1, addr2):
    if addr1 < 0 or addr1 >= NUM_MEMORY_BLOCKS_IN_SOUP:
        return False
    if addr2 < 0 or addr2 >= NUM_MEMORY_BLOCKS_IN_SOUP:
        return False

    cut = list(simData.soup.cut(MEM_BLOCK_LEN))
    
    block1 = cut[addr1]
    block2 = cut[addr2]
    
    #print("swapping ", addr1, addr2, " | ", block1, "<->", block2)
    
    #simData.soup.overwrite(block1, MEM_BLOCK_LEN*addr2)
    #simData.soup.overwrite(block2, MEM_BLOCK_LEN*addr1)
    
    #simData.logBlockUpdate(addr1, wholeBlock=True)
    #simData.logBlockUpdate(addr2, wholeBlock=True)
    simData.setBlock(block1.bin, addr2)
    simData.setBlock(block2.bin, addr1)
    
    return True
    
 
# 
# Other
#

def blocksEquivalent(block1, block2):
    if block1 == None and block2 == None:
        return True
        
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
        
    keyName = key["body"]["code"]
    if not (keyName[0:3] == "KEY" or keyName == "CLMk"):
        return False
        
    return True
    

# returns true if the lock really == a lock, false otherwise
def lockCheck(lock):
    if not lock["header"]["type"] == "instruction":
        return False
        
    lockName = lock["body"]["code"]
    if not (lockName[0:3] == "LOK" or lockName == "CLAM"):
        return False
        
    return True
   
   
def keyLockMatch(key, lock):
    if not keyCheck(key) or not lockCheck(lock):
        return False
        
    if key["body"]["code"][3] == lock["body"]["code"][3]:
        return True
        
    if key["body"]["code"] == "CLMk" and lock["body"]["code"] == "CLAM":
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
    
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
