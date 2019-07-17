from Main import SimulationData
import utils


def noOp(simData, executorAddress, myAddress):
    return {}
    
    
def jumpR(simData, executorAddress, myAddress, arg0):
    reg = utils.readBlock(utils.findRegister(simData, executorAddress, arg0))
    if reg is None or reg["body"] < 0 or reg["body"] > NUM_MEM_BLOCKS_IN_SOUP:
        return {"fault": True}
    return {"jump": reg["body"]}
    
    
def jumpB(simData, executorAddress, myAddress):
    key = utils.readBlock(sim.soup, myAddress+1)
    if not utils.keyCheck(key):
        return {"fault": True}
    
    i = myAddress
    while i >= 0:
        block = utils.readBlock(i)
        if utils.keyLockMatch(key, block)
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
        if utils.keyLockMatch(key, block)
            return {"jump": i}
        i += 1
    
    return {"fault": True}
    
    
def addressOfJumpB(simData, executorAddress, myAddress, arg0):
    val = jumpB(simData, executorAddress, myAddress)
    if "fault" in val and val["fault"] is True:
        return {"fault": True}
    
    regAddress = utils.findRegister(simData.soup, executorAddress, arg0)
    success = utils.registerWrite(simData.soup, executorAddress, regAddress)
    
    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}
    
    
def addressOfJumpF(simData, executorAddress, myAddress, arg0):
    val = jumpF(simData, executorAddress, myAddress)
    if "fault" in val and val["fault"] is True:
        return {"fault": True}
    
    regAddress = utils.findRegister(simData.soup, executorAddress, arg0)
    success = utils.registerWrite(simData.soup, executorAddress, regAddress)
    
    if success:
        return {}
    else:
        return {"fault": True, "executor deinit": executorAddress}
    
    
def skipIfZero(simData, executorAddress, myAddress, arg0):
    register = utils.readRegister(simData.soup, executorAddress, arg0)
    
    if register is None:
        return {"fault": True}
    
    if register["body"] is 0:
        return {"ip increment": 2}
    return {}    
        
        
def skipIfNull(simData, executorAddress, myAddress, arg0):
    register = utils.readRegister(simData.soup, executorAddress, arg0)
    
    if register is None:
        return {"fault": True}
    
    if register["body"] is None:
        return {"ip increment": 2}
    return {}    
        
    
def skipUnlessEquiv(simData, executorAddress, myAddress, arg0, arg1):
    register1 = utils.readRegister(simData.soup, executorAddress, arg0)
    register2 = utils.readRegister(simData.soup, executorAddress, arg1)
    
    if register1 is None or register2 is None:
        return {"fault": True}
    
    ins1 = readBlock(simData.soup, register1["body"])
    ins2 = readBlock(simData.soup, register1["body"])
        
    if ins1 is None:
        return {"fault": True}
    if ins2 is None:
        return {"fault": True}
        
    if ins1["symbol"] == ins2["symbol"]:
        return {}
    return {"ip increment": 2}
    
 
def add(simData, executorAddress, myAddress, arg0, arg1, arg2):
    addr1 = utils.findRegister(simData.soup, executorAddress, arg0)
    addr2 = utils.findRegister(simData.soup, executorAddress, arg1)
    addr3 = utils.findRegister(simData.soup, executorAddress, arg2)
    
    reg1 = utils.readBlock(simData.soup, addr1)
    reg1 = utils.readBlock(simData.soup, addr1)
    reg1 = utils.readBlock(simData.soup, addr1)
    
    
def initExecutor():
    return {"executor init": addr}
    
    
def deinitExecutor():
    return {"executor deinit": addr}
    

def swapInstructions():
    return {"active executor move": (fromAddr, toAddr)}
    
    
def ifNotZero():
    return {"ip increment": 2}
    

def skipUnlessEquiv():
    return {"checked address": } 
