
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
    if blockIndex < 0 or blockIndex >=  NUM_BLOCKS_IN_SOUP
        return None
        
    block = soup.cut(MEM_BLOCK_LEN)[blockIndex]
    header = block[0:HEADER_LEN]
    body = block[HEADER_LEN:]
    
    headerInfo = FLAG_CODES[header.bin[2:]]
    bodyInfo   = headerInfo["interpret body"](body.bin[2:])
    
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

def registerWrite(soup, executorAddress, registerAddress, val, unsigned=False):
    if val is None:
        val = readBlock(soup, registerAddress)["body"]
        addToDump(soup, executorAddress, abs(val))
        
        binary = "0b" + intToBinary(0, BODY_LEN, unsigned=unsigned)
        soup.overwrite(binary, registerAddress+HEADER_LEN)
        soup.overwrite("0b"+'010', registerAddress)
        return
        
    # take the neccessary difference from the dump register
    oldVal = readBlock(soup, registerAddress)["body"]
    diff = abs(val) - abs(oldVal)
    success = takeFromDump(soup, executorAddress, diff)
    
    if not success:
        killExecutor(soup, executorAddress)
    
    # the actual writing
    binary = "0b" + intToBinary(val, BODY_LEN, unsigned=unsigned)
    soup.overwrite(binary, registerAddress+HEADER_LEN)
        

# returns False if there was an error
def takeFromDump(soup, executorAddress, val):
    dumpAddr = findDump(soup, executorAddress)
    
    if dumpAddr == -1:
        return False
    
    dump = readBlock(soup, dumpAddr)
    
    if val > dump["body"]:
        return False
        
    binary = "0b" + intToBinary(dump["body"] - val, BODY_LEN, unsigned=unsigned)
    soup.overwrite(binary, dumpAddr+HEADER_LEN)
    
    return True


def addToDump(soup, executorAddress, val):
    return takeFromDump(soup, executorAddress, -val)
    

def killExecutor(soup, executorAddress):
    binary = "0b" + '100'
    soup.overwrite(binary, executorAddress)
        

def awakenExecutor(soup, executorAddress):
    binary = "0b" + '101'
    soup.overwrite(binary, executorAddress)
 
 
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
