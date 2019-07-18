
import const
from const import *

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
    
    return binaryToInt(binary, bitLen, unsigned=unsigned)
    
    
def bitwiseShiftLeft(intVal, bitLen, unsigned=False):
    assert(type(intVal) == int)    
    binary = intToBinary(intVal, bitLen, unsigned=unsigned)
    binary = binary[1:] + binary[-1]
    
    return binaryToInt(binary, bitLen, unsigned=unsigned)
    
    
def bitwiseShiftRight(intVal, bitLen, unsigned=False):
    assert(type(intVal) == int)    
    binary = intToBinary(intVal, bitLen, unsigned=unsigned)
    binary = binary[0] + binary[0:-1]
    
    return binaryToInt(binary, bitLen, unsigned=unsigned)
    
  
def bitwiseAND(intVal1, intVal2, bitLen, unsigned=False):
    assert(type(intVal1) == int)   
    assert(type(intVal2) == int)    
    
    binary1 = [bit == '1' for bit in intToBinary(intVal1, bitLen, unsigned=unsigned)]
    binary2 = [bit == '1' for bit in intToBinary(intVal2, bitLen, unsigned=unsigned)]
    
    binary = ''.join('1' if (a and b) else '0' for a, b in zip(binary1, binary2))
    
    return binaryToInt(binary, bitLen, unsigned=unsigned)
    
   
def bitwiseOR(intVal1, intVal2, bitLen, unsigned=False):
    assert(type(intVal1) == int)   
    assert(type(intVal2) == int)    
    
    binary1 = [bit == '1' for bit in intToBinary(intVal1, bitLen, unsigned=unsigned)]
    binary2 = [bit == '1' for bit in intToBinary(intVal2, bitLen, unsigned=unsigned)]
    
    binary = ''.join('1' if (a or b) else '0' for a, b in zip(binary1, binary2))
    
    return binaryToInt(binary, bitLen, unsigned=unsigned)
    
     
def bitwiseXOR(intVal1, intVal2, bitLen, unsigned=False):
    assert(type(intVal1) == int)   
    assert(type(intVal2) == int)    
    
    binary1 = [bit == '1' for bit in intToBinary(intVal1, bitLen, unsigned=unsigned)]
    binary2 = [bit == '1' for bit in intToBinary(intVal2, bitLen, unsigned=unsigned)]
    
    binary = ''.join('1' if (a != b) else '0' for a, b in zip(binary1, binary2))
    
    return binaryToInt(binary, bitLen, unsigned=unsigned)
    
         
#
# Non-modifying utility functions
#
def findDump(simData, executorAddress):
    addr = executorAddress+1
    
    while addr < NUM_MEMORY_BLOCKS_IN_SOUP:
        block = readBlock(simData, addr)
        if block["header"]["name"] == "dump register":
            return addr
        
    return -1


def findRegister(simData, executorAddress, regNum):
    regCount = -1
    addr = executorAddress+1
    
    while addr < NUM_MEMORY_BLOCKS_IN_SOUP:
        block = readBlock(simData, addr)
        if block["header"]["type"] == "register":
            regCount += 1
        
        if regCount == regNum:
            return addr
        addr += 1
        
    return -1


def readBlock(simData, blockIndex):
    import opcode
    from opcode import FLAG_CODES
    
    if blockIndex < 0 or blockIndex >= NUM_MEMORY_BLOCKS_IN_SOUP:
        print("readBlock: index out of bounds ", blockIndex, " max val ", NUM_MEMORY_BLOCKS_IN_SOUP)
        return None
        
    block = list(simData.soup.cut(MEM_BLOCK_LEN))[blockIndex]
    block = block.bin
    header = block[0:HEADER_LEN]
    body = block[HEADER_LEN:]
    
    headerInfo = FLAG_CODES[header].copy()
    bodyInfo   = headerInfo["interpret body"](body)
    
    if headerInfo["symbol"] == None:
        headerInfo["symbol"] = bodyInfo["symbol"]
        
    return {"header": headerInfo, "body": bodyInfo}


def readRegister(simData, executorAddress, regNum):
    regAddress = findRegister(simData, executorAddress, regNum)
    return readBlock(simData, regAddress)
    

def decodeArgs(simData, address, count):
    queue = [0,1,2,3,4,5,6,7,8,9]
    arglist = []
    
    # the acceptMemArgs variable is used to make sure that only consecutive arguments are considered
    # ie: 
    # +235    here, all arguments are counted
    # +3u56   here, only the 3 is counted
    # +x863   here, no arguments are counted
    # without the acceptMemArgs variable, in all three examples, all 3 arguments would be counted
    acceptMemArgs = True
    for i in range(1, block["body"]["arg count"]+1):
        if acceptMemArgs:
            nextMemArg = readBlock(blockAddress + i)
            if nextMemArg["header"]["type"] == "instruction" and nextMemArg["body"]["code"][0:3] == "ARG":
                arg = int(nextMemArg["body"]["code"][3])
                arglist.append(arg)
                queue.remove(arg)
            else:
                acceptMemArgs = False
                arglist.append(queue.pop())
        else:
            arglist.append(queue.pop())
            
    return arglist

     
#
# Modifying utility functions
#
def registerWriteIgnoreDumpMechanics(simData, registerAddress, val, unsigned=False):
    binary = "0b" + intToBinary(val, BODY_LEN, unsigned=unsigned)
    simData.soup.overwrite(binary, MEM_BLOCK_LEN*registerAddress+HEADER_LEN)
    return 


def registerWrite(simData, executorAddress, registerAddress, val, unsigned=False):
    if val == None:
        val = readBlock(simData, registerAddress)["body"]
        addToDump(simData, executorAddress, abs(val))
        
        binary = "0b" + '0'*BODY_LEN 
        simData.soup.overwrite(binary, MEM_BLOCK_LEN*registerAddress+HEADER_LEN)
        simData.soup.overwrite("0b"+'010', MEM_BLOCK_LEN*registerAddress)
        return
        
    # take the neccessary difference from the dump register
    oldVal = readBlock(simData, registerAddress)["body"]
    diff = abs(val) - abs(oldVal)
    success = takeFromDump(simData, executorAddress, diff)
    
    if not success:
        return False
    
    # the actual writing
    binary = "0b" + intToBinary(val, BODY_LEN, unsigned=unsigned)
    simData.soup.overwrite(binary, MEM_BLOCK_LEN*registerAddress+HEADER_LEN)
       
    print(oldVal, " -> ", readBlock(simData, registerAddress)["body"])   
        
    return True    


def registerInitialize(simData, registerAddress):
    block = readBlock(simData, registerAddress)
    assert(block["header"]["name"] == "register with a null value")
    
    simData.soup.overwrite("0b"+'011' + ('0'*BODY_LEN), MEM_BLOCK_LEN*registerAddress)


# returns False if there was an error
def takeFromDump(simData, executorAddress, val):
    dumpAddr = findDump(simData, executorAddress)
    
    if dumpAddr == -1:
        return False
    
    dump = readBlock(simData, dumpAddr)
    
    if val > dump["body"]:
        return False
        
    binary = "0b" + intToBinary(dump["body"] - val, BODY_LEN, unsigned=True)
    simData.soup.overwrite(binary, MEM_BLOCK_LEN*dumpAddr+HEADER_LEN)
    
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
    binary = "0b" + '100'
    simData.soup.overwrite(binary, MEM_BLOCK_LEN*executorAddress)
        

def awakenExecutor(simData, executorAddress):
    binary = "0b" + '101'
    simData.soup.overwrite(binary, MEM_BLOCK_LEN*executorAddress)
 

def swapMemoryBlocks(simData, addr1, addr2):
    cut = simData.soup.cut(MEM_BLOCK_LEN)
    
    block1 = cut[addr1].bin
    block2 = cut[addr2].bin
    
    simData.soup.overwrite(block1, MEM_BLOCK_LEN*addr2)
    simData.soup.overwrite(block2, MEM_BLOCK_LEN*addr2)
    
 
#
# Other
#

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
    
    
def getClaimData(simData, executorAddress):
    boundaries = getClaimBoundaries(simData, executorAddress)
    blocks = [readBlock(simData, i) for i in range(boundaries[0], boundaries[1]+1)]
    
    symbolString = ''.join(e["header"]["symbol"] for e in blocks)
    registerValues = [block["body"] for block in blocks if block["header"]["type"] == "register"]
    dumpRegisterValues = [block["body"] for block in blocks if block["header"]["type"] == "dump register"]
    ip = readBlock(simData, executorAddress)["body"]

    return {
        "executor address": executorAddress,
        "boundaries": boundaries,
        "symbols": symbolString,
        "register values": registerValues,
        "dump register values": dumpRegisterValues,
        "instruction pointer": ip
        }
    
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
