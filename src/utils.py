
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
    assert(type(intVal) is int)    
    binary = intToBinary(intVal, bitLen, unsigned=unsigned)
    binary = ''.join('1' if bit is '0' else '0' for bit in binary)
    
    return binaryToInt(binary, bitLen, unsigned=unsigned)
    
    
def bitwiseShiftLeft(intVal, bitLen, unsigned=False):
    assert(type(intVal) is int)    
    binary = intToBinary(intVal, bitLen, unsigned=unsigned)
    binary = binary[1:] + binary[-1]
    
    return binaryToInt(binary, bitLen, unsigned=unsigned)
    
    
def bitwiseShiftRight(intVal, bitLen, unsigned=False):
    assert(type(intVal) is int)    
    binary = intToBinary(intVal, bitLen, unsigned=unsigned)
    binary = binary[0] + binary[0:-1]
    
    return binaryToInt(binary, bitLen, unsigned=unsigned)
    
  
def bitwiseAND(intVal1, intVal2, bitLen, unsigned=False):
    assert(type(intVal1) is int)   
    assert(type(intVal2) is int)    
    
    binary1 = [bit is '1' for bit in intToBinary(intVal1, bitLen, unsigned=unsigned)]
    binary2 = [bit is '1' for bit in intToBinary(intVal2, bitLen, unsigned=unsigned)]
    
    binary = ''.join('1' if (a and b) else '0' for a, b in zip(binary1, binary2))
    
    return binaryToInt(binary, bitLen, unsigned=unsigned)
    
   
def bitwiseOR(intVal1, intVal2, bitLen, unsigned=False):
    assert(type(intVal1) is int)   
    assert(type(intVal2) is int)    
    
    binary1 = [bit is '1' for bit in intToBinary(intVal1, bitLen, unsigned=unsigned)]
    binary2 = [bit is '1' for bit in intToBinary(intVal2, bitLen, unsigned=unsigned)]
    
    binary = ''.join('1' if (a or b) else '0' for a, b in zip(binary1, binary2))
    
    return binaryToInt(binary, bitLen, unsigned=unsigned)
    
     
def bitwiseXOR(intVal1, intVal2, bitLen, unsigned=False):
    assert(type(intVal1) is int)   
    assert(type(intVal2) is int)    
    
    binary1 = [bit is '1' for bit in intToBinary(intVal1, bitLen, unsigned=unsigned)]
    binary2 = [bit is '1' for bit in intToBinary(intVal2, bitLen, unsigned=unsigned)]
    
    binary = ''.join('1' if (a is not b) else '0' for a, b in zip(binary1, binary2))
    
    return binaryToInt(binary, bitLen, unsigned=unsigned)
    
         
#
# Non-modifying utility functions
#
def findDump(soup, executorAddress):
    addr = executorAddress+1
    
    while addr < NUM_MEMORY_BLOCKS_IN_SOUP:
        block = readBlock(simData, addr)
        if block["header"]["name"] is "dump register":
            return addr
        
    return -1


def findRegister(soup, executorAddress, regNum):
    regCount = -1
    addr = executorAddress+1
    
    while addr < NUM_MEMORY_BLOCKS_IN_SOUP:
        block = readBlock(simData, addr)
        if block["header"]["type"] is "register":
            regCount += 1
        
        if regCount == regNum:
            return addr
        addr += 1
        
    return -1


def readBlock(soup, blockIndex):
    import opcode
    from opcode import FLAG_CODES
    
    if blockIndex < 0 or blockIndex >=  NUM_MEMORY_BLOCKS_IN_SOUP:
        return None
        
    block = list(soup.cut(MEM_BLOCK_LEN))[blockIndex]
    block = block.bin
    header = block[0:HEADER_LEN]
    body = block[HEADER_LEN:]
    
    headerInfo = FLAG_CODES[header].copy()
    bodyInfo   = headerInfo["interpret body"](body)
    
    if headerInfo["symbol"] is None:
        headerInfo["symbol"] = bodyInfo["symbol"]
        
    return {"header": headerInfo, "body": bodyInfo}


def readRegister(soup, executorAddress, regNum):
    regAddress = findRegister(soup, executorAddress, regNum)
    return readBlock(soup, regAddress)
    

def decodeArgs(soup, address, count):
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
            if nextMemArg["header"]["type"] == "instruction" and nextMemArg["body"]["name"][0:3] == "ARG":
                arg = int(nextMemArg["body"]["name"][3])
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
def registerWriteIgnoreDumpMechanics(soup, executorAddress, registerAddress, val, unsigned=False):
    binary = "0b" + intToBinary(val, BODY_LEN, unsigned=unsigned)
    soup.overwrite(binary, MEM_BLOCK_LEN*registerAddress+HEADER_LEN)
    return 


def registerWrite(soup, executorAddress, registerAddress, val, unsigned=False):
    if val is None:
        val = readBlock(soup, registerAddress)["body"]
        addToDump(soup, executorAddress, abs(val))
        
        binary = "0b" + '0'*BODY_LEN 
        soup.overwrite(binary, MEM_BLOCK_LEN*registerAddress+HEADER_LEN)
        soup.overwrite("0b"+'010', MEM_BLOCK_LEN*registerAddress)
        return
        
    # take the neccessary difference from the dump register
    oldVal = readBlock(soup, registerAddress)["body"]
    diff = abs(val) - abs(oldVal)
    success = takeFromDump(soup, executorAddress, diff)
    
    if not success:
        return False
    
    # the actual writing
    binary = "0b" + intToBinary(val, BODY_LEN, unsigned=unsigned)
    soup.overwrite(binary, MEM_BLOCK_LEN*registerAddress+HEADER_LEN)
        
    return True    


def registerInitialize(soup, registerAddress):
    block = readBlock(soup, registerAddress)
    assert(block["header"]["name"] == "register with a null value")
    
    soup.overwrite("0b"+'011' + ('0'*BODY_LEN), MEM_BLOCK_LEN*registerAddress)


# returns False if there was an error
def takeFromDump(soup, executorAddress, val):
    dumpAddr = findDump(soup, executorAddress)
    
    if dumpAddr == -1:
        return False
    
    dump = readBlock(soup, dumpAddr)
    
    if val > dump["body"]:
        return False
        
    binary = "0b" + intToBinary(dump["body"] - val, BODY_LEN, unsigned=unsigned)
    soup.overwrite(binary, MEM_BLOCK_LEN*dumpAddr+HEADER_LEN)
    
    return True


def addToDump(soup, executorAddress, val):
    return takeFromDump(soup, executorAddress, -val)
    

def stackPush(soup, executorAddress, stackAddress, val):
    addr = stackAddress+1
    block = readBlock(soup, addr)
    
    while block is not None and block["header"]["type"] is "register":
        if block["name"] is "register with a null value":
            registerInitialize(soup, addr)
            return registerWrite(soup, executorAddress, val)
        addr += 1
        block = readBlock(soup, addr)
    return 'fail safe'
        

def stackPop(soup, executorAddress, stackAddress, registerAddress):
    addr = stackAddress+1
    block = readBlock(soup, addr)
    
    while block is not None and block["header"]["type"] is "register":
        if block["name"] is "register with a null value":
            break
        addr += 1
        block = readBlock(soup, addr)
    
    addr -= 1
    block = readBlock(soup, addr)

    if block is None or block["header"]["name"] is not "register":    
        return 'fail safe'
        
    val = block["body"]
    registerWrite(soup, executorAddress, addr, None) # always successful
    return registerWrite(soup, executorAddress, registerAddress, val)
        

def killExecutor(soup, executorAddress):
    binary = "0b" + '100'
    soup.overwrite(binary, MEM_BLOCK_LEN*executorAddress)
        

def awakenExecutor(soup, executorAddress):
    binary = "0b" + '101'
    soup.overwrite(binary, MEM_BLOCK_LEN*executorAddress)
 

def swapMemoryBlocks(soup, addr1, addr2):
    cut = soup.cut(MEM_BLOCK_LEN)
    
    block1 = cut[addr1].bin
    block2 = cut[addr2].bin
    
    soup.overwrite(block1, MEM_BLOCK_LEN*addr2)
    soup.overwrite(block2, MEM_BLOCK_LEN*addr2)
    
 
#
# Other
#

# returns true if the key really is a key, false otherwise
def keyCheck(key):
    if not key["header"]["type"] is "instruction":
        return False
        
    keyName = key["body"]["name"]
    if not (keyName[0:3] is "KEY" or keyName is "CLMk"):
        return False
        
    return True
    

# returns true if the lock really is a lock, false otherwise
def lockCheck(lock):
    if not lock["header"]["type"] is "instruction":
        return False
        
    lockName = lock["body"]["name"]
    if not (lockName[0:3] is "LOK" or lockName is "CLAM"):
        return False
        
    return True
   
   
def keyLockMatch(key, lock):
    if not keyCheck(key) or not lockCheck(lock):
        return False
        
    if key["body"]["name"][3] == lock["body"]["name"][3]:
        return True
        
    if key["body"]["name"] is "CLMk" and lock["body"]["name"] is "CLAM":
        return True
        
    return False
