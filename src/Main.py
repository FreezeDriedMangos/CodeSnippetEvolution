import const
from const import *
from bitstring import BitArray

class SimulationData:
    soup = BitArray('0b' + '0'*TOTAL_MEM_LEN)
    executorAddrList = []
    checkedAddresses = [] # list of tuples (checked, checkedBy)

    def addCheckedAddress(addr):
        for a in addr:
            checkedAddresses.insert(a, 0)
            
        while len(checkedAdresses) >= CHECKED_ADDRESS_STACK_SIZE:
            checkedAdresses.pop(-1)
    

class Simulation:
    data = SimulationData()

    def cycle(self):
        for exeAddr in self.data.executorAddrList:
            self.execute(exeAddr)


    def execute(self, executorAddress):    
        executor = utils.readBlock(self.data, executorAddress)
        if executor["header"]["name"] != "executor":
            executorAddrList.remove(executorAddress)
            return
        
        blockAddress = executor["body"]
        block = utils.readBlock(self.data, blockAddress)
        
        if block["header"]["execute?"]:
            args = decodeArgs(self.data, blockAddress, block["body"]["arg count"])
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
                
            utils.registerWrite(self.data, executorAddress, executorAddress, blockAddress, unsigned=True)
            
        elif block["header"]["type"] == "register":
            utils.registerWrite(self.data, executorAddress, blockAddress, 0)
            utils.registerWrite(self.data, executorAddress, executorAddress, blockAddress+1)
        else:
            utils.registerWrite(self.data, executorAddress, executorAddress, blockAddress+1)
    
    
    def init(self, ancestorString):
        import random
        import opcode
        from opcode import SPAWN_LIST
        import compiler
        import utils
    
        # put a random memory block at each location
        for i in range(0, TOTAL_MEM_LEN, MEM_BLOCK_LEN):
            self.data.soup.overwrite('0b'+random.choice(SPAWN_LIST), i)  
        
        # interpret the ancestor string
        ancestor = compiler.compileGenome(ancestorString)
        ancestorData = SimulationData()
        ancestorData.soup = BitArray('0b' + ancestor)
        
        ancestorBlocks = [utils.readBlock(ancestorData, i) for i in range(len(ancestorString))]
        ancestorExecutorLocs = [i for i in range(len(ancestorBlocks)) if ancestorBlocks[i]["header"]["name"] == "executor"]
        
        # seed the soup with one common ancestor
        ancestorLoc = random.randrange(0, NUM_MEMORY_BLOCKS_IN_SOUP-len(ancestor))
        self.data.soup.overwrite('0b'+ancestor, MEM_BLOCK_LEN*ancestorLoc)
        
        
        # find ancestor's executor
        for loc in ancestorExecutorLocs:
            loc = loc + ancestorLoc
            self.data.executorAddrList.append(loc)
            # initialize this executor
            utils.registerWriteIgnoreDumpMechanics(self.data, loc, loc, unsigned=True)
            


if __name__ == "__main__":  
    import pprint  
    pp = pprint.PrettyPrinter(indent=4)

    sim = Simulation()
    sim.init('''T◈▯#####[t]t1r2"23"24B⸘03)c^3(bC$32=01)d^0^2^3(bD^4:4(tT''')       
    #print(sim.data.soup)
    
    import utils
    exeAddr = sim.data.executorAddrList[0]
    #print("executor addr: ", exeAddr)
    pp.pprint(utils.getClaimData(sim.data, exeAddr))
    
    sim.cycle()
    sim.cycle()
    sim.cycle()
    pp.pprint(utils.getClaimData(sim.data, exeAddr))
    
        
