import const

class SimulationData:
    soup = BitArray('0b' + '0'*TOTAL_MEM_LEN)
    executorAddrList = []
    checkedAddresses = [] # list of tuples (checked, checkedBy)

    def addCheckedAddress(addr):
        checkedAddresses.append(*addr)
        while len(checkedAdresses) >= CHECKED_ADDRESS_STACK_SIZE:
            checkedAdresses.pop()
    

class Simulation:
    import random
    import utils
    
    data = SimulationData()

    def execute(self, executorAddress):    
        executor = readBlock(self.data.soup, executorAddress)
        if executor["header"]["name"] is not "executor":
            executorAddrList.remove(executorAddress)
            return
        
        blockAddress = executor["body"]
        block = readBlock(self.data.soup, blockAddress)
        
        if block["header"]["execute?"]:
            args = decodeArgs(self.data.soup, blockAddress, block["body"]["arg count"])
            retval = block["body"]["function"](self.data, executorAddress, blockAddress, *args)
            
            if "checked address" in retval:
                data.addCheckedAddress(retval["checked address"])
            
            # handle executor death, rebirth, and moving
            if "executor init" in retval:
                executorAddrList.append(retval["executor init"])
            if "executor deinit" in retval:
                executorAddrList.remove(retval["executor deinit"])
            if "active executor move" in retval:
                for pair in retval["active executor move"]:
                    executorAddrList.remove(pair[0])
                    executorAddrList.append(pair[1])
            
            # instruction pointer updating
            if "jump" in retval:
                blockAddress = retval["jump"]
            elif "ip increment" in retval:
                blockAddress += retval["ip increment"]
            else:
                blockAddress += 1
                
            registerWrite(self.data.soup, executorAddress, blockAddress, unsigned=True)
            
        elif block["header"]["type"] is "register":
            val = abs(block["body"])
            addToDump(executorAddress, val)
            setRegisterValue(blockAddress, 0)
            setRegisterValue(executorAddress, blockAddress+1)
        else
            setRegisterValue(executorAddress, blockAddress+1)
    
    
    def init(self, ancestor):
        # put a random memory block at each location
        for i in range(0, TOTAL_MEM_LEN, MEM_BLOCK_LEN):
            self.data.soup.overwrite('0b'+random.choice(SPAWN_LIST), i)  
        
        # seed the soup with one common ancestor
        ancestorLoc = random.int(0, TOTAL_MEM_LEN-len(ancestor))
        self.data.soup.overwrite('0b'+ancestor, ancestorLoc)
        
        # find ancestor's executor
        ancestorEx = 0
        executorList.append(ancestorEx)
        
       
        
