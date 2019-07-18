#from Main import SimulationData
import utils


def noOp(simData, executorAddress, myAddress):
    return {}
    
    
def jumpR(simData, executorAddress, myAddress, arg0):
    reg = utils.readBlock(utils.findRegister(simData, executorAddress, arg0))
    if reg == None or reg["body"] < 0 or reg["body"] > NUM_MEM_BLOCKS_IN_SOUP:
        return {"fault": True}
    return {"jump": reg["body"]}
    
    
def jumpB(simData, executorAddress, myAddress):
    key = utils.readBlock(sim.soup, myAddress+1)
    if not utils.keyCheck(key):
        return {"fault": True}
    
    i = myAddress
    while i >= 0:
        block = utils.readBlock(i)
        if utils.keyLockMatch(key, block):
            return {"jump": i}
        i -= 1
    
    return {"fault": True}

    
def jumpF(simData, executorAddress, myAddress):
    key = utils.readBlock(simData, myAddress+1)
    if not utils.keyCheck(key):
        return {"fault": True}
    
    i = myAddress
    while i < TOTAL_MEM_LEN:
        block = utils.readBlock(sim, i)
        if utils.keyLockMatch(key, block):
            return {"jump": i}
        i += 1
    
    return {"fault": True}
    
    
def addressOfJumpB(simData, executorAddress, myAddress, arg0):
    val = jumpB(simData, executorAddress, myAddress)
    if "fault" in val and val["fault"] == True:
        return {"fault": True}
    
    regAddress = utils.findRegister(simData, executorAddress, arg0)
    success = utils.registerWrite(simData, executorAddress, regAddress, val["jump"])
    
    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}
    
    
def addressOfJumpF(simData, executorAddress, myAddress, arg0):
    val = jumpF(simData, executorAddress, myAddress)
    if "fault" in val and val["fault"] == True:
        return {"fault": True}
    
    regAddress = utils.findRegister(simData, executorAddress, arg0)
    success = utils.registerWrite(simData, executorAddress, regAddress, val["jump"])
    
    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}
    
    
def skipIfZero(simData, executorAddress, myAddress, arg0):
    register = utils.readRegister(simData, executorAddress, arg0)
    
    if register == None:
        return {"fault": True}
    
    if register["body"] == 0:
        return {"ip increment": 2}
    return {}    
        
        
def skipIfNull(simData, executorAddress, myAddress, arg0):
    register = utils.readRegister(simData, executorAddress, arg0)
    
    if register == None:
        return {"fault": True}
    
    if register["body"] == None:
        return {"ip increment": 2}
    return {}    


def skipIfDumpIsZero(simData, executorAddress, myAddress):
    addr = utils.findDump(simData, executorAddress)
    dump = utils.readBlock(simData, addr)
    
    if dump == None:
        return {"fault": True}
    
    if dump["body"] == 0:
        return {"ip increment": 2}
    return {}    
                
    
def skipUnlessEquiv(simData, executorAddress, myAddress, arg0, arg1):
    register1 = utils.readRegister(simData, executorAddress, arg0)
    register2 = utils.readRegister(simData, executorAddress, arg1)
    
    if register1 == None or register2 == None:
        return {"fault": True}
    
    ins1 = readBlock(simData, register1["body"])
    ins2 = readBlock(simData, register2["body"])
        
    if ins1 == None:
        return {"fault": True}
    if ins2 == None:
        return {"fault": True}
    
    if ins1["header"]["type"] == "instruction":
        if ins1["symbol"] == ins2["symbol"]:
            return {"checked address": [register1["body"], register2["body"]]}
    elif ins1["header"]["type"] == ins2["header"]["type"]: # will match (live executor, dormant executor) and (register, register with null) pairs
        return {"checked address": [register1["body"], register2["body"]]}
    return {"ip increment": 2, "checked address": [register1["body"], register2["body"]]}
   
    
def skipUnlessEqual(simData, executorAddress, myAddress, arg0, arg1):
    register1 = utils.readRegister(simData, executorAddress, arg0)
    register2 = utils.readRegister(simData, executorAddress, arg1)
    
    if register1 == None or register2 == None:
        return {"fault": True}
    
    if register1["body"] == register2["body"]:
        return {}
    return {"ip increment": 2}
       

def add(simData, executorAddress, myAddress, arg0, arg1, arg2):
    return simpleOp(simData, executorAddress, myAddress, arg0, arg1, arg2, lambda a, b: a+b)


def subtract(simData, executorAddress, myAddress, arg0, arg1, arg2):
    return simpleOp(simData, executorAddress, myAddress, arg0, arg1, arg2, lambda a, b: a-b)


def multiply(simData, executorAddress, myAddress, arg0, arg1, arg2):
    return simpleOp(simData, executorAddress, myAddress, arg0, arg1, arg2, lambda a, b: a*b)


def divide(simData, executorAddress, myAddress, arg0, arg1, arg2):
    return simpleOp(simData, executorAddress, myAddress, arg0, arg1, arg2, lambda a, b: None if b == 0 else a/b)


def bitwiseAND(simData, executorAddress, myAddress, arg0, arg1, arg2):
    return simpleOp(simData, executorAddress, myAddress, arg0, arg1, arg2, lambda a, b: utils.bitwiseAND(a, b, BODY_LEN))

 
def bitwiseOR(simData, executorAddress, myAddress, arg0, arg1, arg2):
    return simpleOp(simData, executorAddress, myAddress, arg0, arg1, arg2, lambda a, b: utils.bitwiseOR(a, b, BODY_LEN))

 
def bitwiseXOR(simData, executorAddress, myAddress, arg0, arg1, arg2):
    return simpleOp(simData, executorAddress, myAddress, arg0, arg1, arg2, lambda a, b: utils.bitwiseXOR(a, b, BODY_LEN))

 
def simpleOp(simData, executorAddress, myAddress, arg0, arg1, arg2, operaton):
    addr = utils.findRegister(simData, executorAddress, arg0)
    reg1 = utils.readBlock(simData, addr)
    reg2 = utils.readRegister(simData, executorAddress, arg1)
    reg3 = utils.readRegister(simData, executorAddress, arg2)
    
    val = operation(reg2["body"], reg3["body"])
    success = utils.registerWrite(simData, addr, val)
    
    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}


def increment(simData, executorAddress, myAddress, arg0):
    addr = utils.findRegister(simData, executorAddress, arg0)
    reg  = utils.readBlock(simData, addr)
    
    success = utils.registerWrite(simData, addr, reg["body"]+1)
    
    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}


def decrement(simData, executorAddress, myAddress, arg0):
    addr = utils.findRegister(simData, executorAddress, arg0)
    reg  = utils.readBlock(simData, addr)
    
    success = utils.registerWrite(simData, addr, reg["body"]-1)
    
    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}

    
def bitwiseInverse(simData, executorAddress, myAddress, arg0):
    addr = utils.findRegister(simData, executorAddress, arg0)
    reg  = utils.readBlock(simData, addr)
    
    inverse = utils.bitwiseInverse(reg["body"], BODY_LEN, unsigned=False)
    
    success = utils.registerWrite(simData, addr, inverse)
    
    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}
        
     
def bitwiseShiftLeft(simData, executorAddress, myAddress, arg0):
    addr = utils.findRegister(simData, executorAddress, arg0)
    reg  = utils.readBlock(simData, addr)
    
    shift = utils.bitwiseShiftLeft(reg["body"], BODY_LEN, unsigned=False)
    
    success = utils.registerWrite(simData, addr, inverse)
    
    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}
        

def bitwiseShiftRight(simData, executorAddress, myAddress, arg0):
    addr = utils.findRegister(simData, executorAddress, arg0)
    reg  = utils.readBlock(simData, addr)
    
    shift = utils.bitwiseShiftRight(reg["body"], BODY_LEN, unsigned=False)
    
    success = utils.registerWrite(simData, addr, inverse)
    
    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}
        

def setToZero(simData, executorAddress, myAddress, arg0):   
    addr = utils.findRegister(simData, executorAddress, arg0)
    success = utils.registerWrite(simData, executorAddress, addr, 0)    

    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}
        
 
def setToOne(simData, executorAddress, myAddress, arg0):   
    addr = utils.findRegister(simData, executorAddress, arg0)
    success = utils.registerWrite(simData, executorAddress, addr, 1)    

    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}
        
        
def setToNull(simData, executorAddress, myAddress, arg0):   
    addr = utils.findRegister(simData, executorAddress, arg0)
    success = utils.registerWrite(simData, executorAddress, addr, None)    

    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}
        


def setToRand(simData, executorAddress, myAddress, arg0):   
    addr = utils.findRegister(simData, executorAddress, arg0)
    success = utils.registerWrite(simData, executorAddress, addr, rand.nextInt(0, NUM_MEM_BLOCKS_IN_SOUP))    

    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}
        

    
def setSelfToZero(simData, executorAddress, myAddress):
    success = utils.registerWrite(simData, executorAddress, myAddress, 0) 
    
    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}
        
    
def copy(simData, executorAddress, myAddress, arg0, arg1):   
    addr0 = utils.findRegister(simData, executorAddress, arg0)
    addr1 = utils.findRegister(simData, executorAddress, arg1)
    
    if addr0 == -1 or addr0 == -1:
        return {"fault": True}
    
    val0 = utils.readBlock(simData, addr0)["body"]   
    
    success = utils.registerWrite(simData, executorAddress, addr1, val0) 
    
    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}
        
    
def swap(simData, executorAddress, myAddress, arg0, arg1):   
    addr1 = utils.findRegister(simData, executorAddress, arg0)
    addr2 = utils.findRegister(simData, executorAddress, arg1)
    
    if addr1 == -1 or addr2 == -1:
        return {"fault": True}
    
    val1 = utils.readBlock(simData, addr1)["body"]   
    val2 = utils.readBlock(simData, addr1)["body"]   

    success1 = utils.registerWriteIgnoreDumpMechanics(simData, executorAddress, addr1, val2) 
    success2 = utils.registerWriteIgnoreDumpMechanics(simData, executorAddress, addr2, val1) 
    
    success = success1 and success2
    
    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}
 
 
def push(simData, executorAddress, myAddress, arg0):
    # find the first matching lock after 
    val = jumpF(simData, executorAddress, executorAddress)
    reg = utils.readRegister(simData, executorAddress, arg0)
    
    if ("fault" in val and val["fault"] == True) or reg == None:
        return {"fault": True}
    
    success = utils.stackPush(simData, executorAddress, val["jump"], reg["body"])
    
    if success == "fail safe":
        return {"fault": True}
    elif success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}
        
 
def pop(simData, executorAddress, myAddress, arg0):   # find the first matching lock after 
    val = jumpF(simData, executorAddress, executorAddress)
    regAddr = utils.findRegister(simData, executorAddress, arg0)
    
    if ("fault" in val and val["fault"] == True) or reg == -1:
        return {"fault": True}
    
    success = utils.stackPop(simData, executorAddress, val["jump"], regAddr)
    
    if success == "fail safe":
        return {"fault": True}
    elif success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}
        

def swapMemoryBlocks(simData, executorAddress, myAddress, arg0, arg1):
    register1 = utils.readRegister(simData, executorAddress, arg0)
    register2 = utils.readRegister(simData, executorAddress, arg1)
    
    if register1 == None or register2 == None:
        return {"fault": True}
    
    ins1 = readBlock(simData, register1["body"])
    ins2 = readBlock(simData, register2["body"])
        
    if ins1 == None:
        return {"fault": True}
    if ins2 == None:
        return {"fault": True}
    
    utils.swapMemoryBlocks(simData, register1["body"], register2["body"])
    
    executorMoves = []
    if ins1["name"] == "executor":
        executorMoves.append(tuple(register1["body"], register2["body"]))
    if ins2["name"] == "executor":
        executorMoves.append(tuple(register2["body"], register1["body"]))
        
    if len(executorMoves) > 0:
        return {"checked address": [register1["body"], register2["body"]], "active executor move": executorMoves}
    return {"checked address": [register1["body"], register2["body"]]}


def monitor(simData, executorAddress, myAddress, arg0, arg1):   
    addr0 = utils.findRegister(simData, executorAddress, arg0)
    addr1 = utils.findRegister(simData, executorAddress, arg1)
        
    claim = utils.findClaim(simData, executorAddress)
    
    for check in simData.checkedAddresses:
        if claim[0] <= check[0] and check[0] <= claim[1]:
            if not (claim[0] <= check[1] and check[1] <= claim[1]):
                # if the check was within claim bounds and wasn't made from within bounds
                success = utils.registerWrite(simData, executorAddress, addr0, claim[0]) and utils.registerWrite(simData, executorAddress, addr1, claim[1])
                
                if success:
                    return {}
                else:
                    return {"fault": True, "executor deinit": executorAddress}
                    
    utils.registerWrite(simData, executorAddress, addr0, None)
    utils.registerWrite(simData, executorAddress, addr1, None)
    return {}
    
    
def initializeExecutor(simData, executorAddress, myAddress, arg0):
    reg = utils.readRegister(simData, executorAddress, arg0)
    block = utils.readBlock(simData, reg["body"])
    
    if block == None or block["name"] != "dormant executor":
        return {"fault": True}
    return {"executor init": reg["body"]}
    
    
def denitializeExecutor(simData, executorAddress, myAddress, arg0):
    reg = utils.readRegister(simData, executorAddress, arg0)
    block = utils.readBlock(simData, reg["body"])
    
    if block == None or block["name"] != "executor":
        return {"fault": True}
    return {"executor deinit": reg["body"]}
    
    

    

