#from Main import SimulationData
import utils
import const
from const import *


def fault(simData, executorAddress, myAddress):
    return {"fault":True}
    

def noOp(simData, executorAddress, myAddress):
    return {}
    
    
def jumpR(simData, executorAddress, myAddress, arg0):
    reg = utils.readBlock(simData, utils.findRegister(simData, executorAddress, arg0))
    if reg == None or reg["body"] < 0 or reg["body"] > NUM_MEM_BLOCKS_IN_SOUP:
        return {"fault": True}
    return {"jump": reg["body"]}
    
    
def jumpB(simData, executorAddress, myAddress):
    key = utils.readBlock(simData, myAddress+1)
    if not utils.keyCheck(key):
        return {"fault": True}
    
    i = myAddress
    while i >= 0:
        block = utils.readBlock(simData, i)
        if utils.keyLockMatch(key, block):
            return {"jump": i}
        i -= 1
    
    return {"fault": True}

    
def jumpF(simData, executorAddress, myAddress):
    key = utils.readBlock(simData, myAddress+1)
    if not utils.keyCheck(key):
        return {"fault": True}
    
    i = myAddress
    while i < NUM_MEMORY_BLOCKS_IN_SOUP:
        block = utils.readBlock(simData, i)
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
    
    
def addressOfInstructionB(simData, executorAddress, myAddress, arg0, arg1, arg2): 
    storeAddress = utils.findRegister(simData, executorAddress, arg2)
    
    reg0 = utils.readRegister(simData, executorAddress, arg0)
    reg1 = utils.readRegister(simData, executorAddress, arg1)
    
    if reg0 == None or reg1 == None or storeAddress == -1:
        return {"fault": True}
    
    addressOfSearchTarget = reg1["body"]
    searchTarget = utils.readBlock(simData, addressOfSearchTarget)
    
    addr = reg0["body"]
    block = utils.readBlock(simData, addr)
    
    if searchTarget is None or block is None or type(addr) != int:
        return {"fault": True}
    
    while not utils.blocksEquivalent(block, searchTarget):
        addr -= 1
        try:
            block = utils.readBlock(simData, addr)
        except:
            print("failed attempted read at ", addr)
            raise
        
        if block is None:
            # writing null is always successful
            utils.registerWrite(simData, executorAddress, storeAddress, None)
            return {}
    
    success = utils.registerWrite(simData, executorAddress, storeAddress, addr)
    
    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress, "details": "Register write failed due to lack of material in dump"}
  
    
def addressOfInstructionF(simData, executorAddress, myAddress, arg0, arg1, arg2): 
    storeAddress = utils.findRegister(simData, executorAddress, arg2)
    
    reg0 = utils.readRegister(simData, executorAddress, arg0)
    reg1 = utils.readRegister(simData, executorAddress, arg1)
    
    if reg0 == None or reg1 == None or storeAddress == -1:
        return {"fault": True}
    
    addressOfSearchTarget = reg1["body"]
    searchTarget = utils.readBlock(simData, addressOfSearchTarget)
    
    addr = reg0["body"]
    block = utils.readBlock(simData, addr)
    
    if searchTarget is None or block is None or type(addr) != int:
        return {"fault": True}
    
    while not utils.blocksEquivalent(block, searchTarget):
        addr += 1
        try:
            block = utils.readBlock(simData, addr)
        except:
            print("failed attempted read at ", addr)
            raise
        
        if block is None:
            # writing null is always successful
            utils.registerWrite(simData, executorAddress, storeAddress, None)
            return {}
    
    success = utils.registerWrite(simData, executorAddress, storeAddress, addr)
    
    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress, "details": "Register write failed due to lack of material in dump"}
        
    
def skipIfZero(simData, executorAddress, myAddress, arg0):
    register = utils.readRegister(simData, executorAddress, arg0)
    
    if register == None:
        return {"fault": True}
    
    if register["body"] == 0:
        return {"skip": 1}
    return {}    
        

def skipUnlessZero(simData, executorAddress, myAddress, arg0):
    register = utils.readRegister(simData, executorAddress, arg0)
    
    if register == None:
        return {"fault": True}
    
    if register["body"] == 0:
        return {}
    return {"skip": 1}          

        
def skipIfNull(simData, executorAddress, myAddress, arg0):
    register = utils.readRegister(simData, executorAddress, arg0)
    
    if register == None:
        return {"fault": True}
    
    if register["body"] == None:
        return {"skip": 1}
    return {}    


def skipUnlessNull(simData, executorAddress, myAddress, arg0):
    register = utils.readRegister(simData, executorAddress, arg0)
    
    if register == None:
        return {"fault": True}
    
    if register["body"] == None:
        return {}
    return {"skip": 1}    


def skipIfDumpIsZero(simData, executorAddress, myAddress):
    addr = utils.findDump(simData, executorAddress)
    dump = utils.readBlock(simData, addr)
    
    if dump == None:
        return {"fault": True}
    
    if dump["body"] == 0:
        return {"skip": 1}
    return {}    
           
           
def skipUnlessDumpIsLessThan(simData, executorAddress, myAddress, arg0):
    register = utils.readRegister(simData, executorAddress, arg0)
    
    if register == None or type(register["body"]) != int:
        return {"fault": True}
    
    addr = utils.findDump(simData, executorAddress)
    dump = utils.readBlock(simData, addr)
    
    if dump == None:
        return {"fault": True}
    
    if dump["body"] < register["body"]:
        return {}
    return {"skip": 1}    
                
    
def skipUnlessEquiv(simData, executorAddress, myAddress, arg0, arg1):
    register1 = utils.readRegister(simData, executorAddress, arg0)
    register2 = utils.readRegister(simData, executorAddress, arg1)
    
    if register1 == None or register2 == None:
        return {"fault": True}
    
    ins1 = utils.readBlock(simData, register1["body"])
    ins2 = utils.readBlock(simData, register2["body"])
        
    if ins1 == None:
        return {"fault": True}
    if ins2 == None:
        return {"fault": True}
    
    #print(ins1["header"]["symbol"], "=?=", ins2["header"]["symbol"])
    
    if utils.blocksEquivalent(ins1, ins2):
        return {"checked address": [register1["body"], register2["body"]]}
    return {"skip": 1, "checked address": [register1["body"], register2["body"]]}
   
    
def skipUnlessEqual(simData, executorAddress, myAddress, arg0, arg1):
    register1 = utils.readRegister(simData, executorAddress, arg0)
    register2 = utils.readRegister(simData, executorAddress, arg1)
    
    if register1 == None or register2 == None:
        return {"fault": True}
    
    if register1["body"] == register2["body"]:
        return {}
    return {"skip": 1}
       

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


def simpleOp(simData, executorAddress, myAddress, arg0, arg1, arg2, operation):
    addr = utils.findRegister(simData, executorAddress, arg0)
    reg2 = utils.readRegister(simData, executorAddress, arg1)
    reg3 = utils.readRegister(simData, executorAddress, arg2)
    
    val = None
    try:
        val = operation(reg2["body"], reg3["body"])
    except:
        print("SimpleOp error, failed safe: ", operation, " on vals ", reg2["body"], reg3["body"])
        val = None
        
    success = utils.registerWrite(simData, executorAddress, addr, val)
    
    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}


def increment(simData, executorAddress, myAddress, arg0):
    addr = utils.findRegister(simData, executorAddress, arg0)
    reg  = utils.readBlock(simData, addr)
    
    if reg["body"] is None:
        return {"fault": True}
    
    success = utils.registerWrite(simData, executorAddress, addr, reg["body"]+1)
    
    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}


def decrement(simData, executorAddress, myAddress, arg0):
    addr = utils.findRegister(simData, executorAddress, arg0)
    reg  = utils.readBlock(simData, addr)
    
    if reg["body"] is None:
        return {"fault": True}
    
    success = utils.registerWrite(simData, executorAddress, addr, reg["body"]-1)
    
    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}

    
def bitwiseInverse(simData, executorAddress, myAddress, arg0):
    addr = utils.findRegister(simData, executorAddress, arg0)
    reg  = utils.readBlock(simData, addr)
    
    inverse = utils.bitwiseInverse(reg["body"], BODY_LEN, unsigned=False)
    
    success = utils.registerWrite(simData, executorAddress, addr, inverse)
    
    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}
        
     
def bitwiseShiftLeft(simData, executorAddress, myAddress, arg0):
    addr = utils.findRegister(simData, executorAddress, arg0)
    reg  = utils.readBlock(simData, addr)
    
    shift = utils.bitwiseShiftLeft(reg["body"], BODY_LEN, unsigned=False)
    
    success = utils.registerWrite(simData, executorAddress, addr, shift)
    
    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}
        

def bitwiseShiftRight(simData, executorAddress, myAddress, arg0):
    addr = utils.findRegister(simData, executorAddress, arg0)
    reg  = utils.readBlock(simData, addr)
    
    shift = utils.bitwiseShiftRight(reg["body"], BODY_LEN, unsigned=False)
    
    success = utils.registerWrite(simData, executorAddress, addr, shift)
    
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
        return {"fault": True, "executor deinit": executorAddress, "details": "This failure was unexpected. "}
        


def setToRand(simData, executorAddress, myAddress, arg0): 
    import random  
    addr = utils.findRegister(simData, executorAddress, arg0)
    success = utils.registerWrite(simData, executorAddress, addr, random.randrange(0, NUM_MEMORY_BLOCKS_IN_SOUP))    

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

    # we're ignoring dump mechanics because we're simply swapping
    # the values of two registers, not adding new value
    utils.registerWriteIgnoreDumpMechanics(simData, addr1, val2) 
    utils.registerWriteIgnoreDumpMechanics(simData, addr2, val1) 
    
    return {}

 
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
    
    ins1 = utils.readBlock(simData, register1["body"])
    ins2 = utils.readBlock(simData, register2["body"])
        
    if ins1 == None:
        return {"fault": True}
    if ins2 == None:
        return {"fault": True}
    
    success = utils.swapMemoryBlocks(simData, register1["body"], register2["body"])
    
    if not success:
        return {"fault": True}
    
    executorMoves = []
    if ins1["header"]["name"] == "executor":
        executorMoves.append((register1["body"], register2["body"], ))
    if ins2["header"]["name"] == "executor":
        executorMoves.append((register2["body"], register1["body"], ))
        
    if len(executorMoves) > 0:
        return {"checked address": [register1["body"], register2["body"]], "active executor move": executorMoves}
    return {"checked address": [register1["body"], register2["body"]]}


def monitor(simData, executorAddress, myAddress, arg0, arg1):   
    addr0 = utils.findRegister(simData, executorAddress, arg0)
    addr1 = utils.findRegister(simData, executorAddress, arg1)
        
    claim = utils.getClaimBoundaries(simData, executorAddress)
    
    checkMade = None
    for check in simData.checkedAddresses:
        if claim[0] <= check[0] and check[0] <= claim[1]:
            if not (claim[0] <= check[1] and check[1] <= claim[1]):
                # if the check was within claim bounds and wasn't made from within bounds
                checkMade = check
                break
    
    if checkMade is not None:
        success = utils.registerWrite(simData, executorAddress, addr0, claim[0]) and utils.registerWrite(simData, executorAddress, addr1, claim[1])
        
        if success:
            return {}
        else:
            return {"fault": True, "executor deinit": executorAddress}
    else:
        utils.registerWrite(simData, executorAddress, addr0, None)
        utils.registerWrite(simData, executorAddress, addr1, None)
        return {}
    
    
def initializeExecutor(simData, executorAddress, myAddress, arg0):
    reg = utils.readRegister(simData, executorAddress, arg0)
    block = utils.readBlock(simData, reg["body"])
    
    if block == None or block["header"]["name"] != "dormant executor":
        return {"fault": True}
    return {"executor init": reg["body"]}
    
    
def denitializeExecutor(simData, executorAddress, myAddress, arg0):
    reg = utils.readRegister(simData, executorAddress, arg0)
    block = utils.readBlock(simData, reg["body"])
    
    if block == None or block["header"]["name"] != "executor":
        return {"fault": True}
    return {"executor deinit": reg["body"]}
    
    

    

