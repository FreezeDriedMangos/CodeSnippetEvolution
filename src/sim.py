import const
from const import *
from bitstring import BitArray

class SimulationData:
    soup = BitArray('0b' + '0'*TOTAL_MEM_LEN)
    executorAddrList = []
    checkedAddresses = [] # list of tuples (checked, checkedBy)
    
    # recording updates
    _blockBodyUpdates = []
    _blockUpdates = []
    
    _mutationLocations = []
    
    
    def addCheckedAddresses(self, addr):
        for a in addr:
            self.checkedAddresses.insert(a, 0)
            
        while len(self.checkedAddresses) >= CHECKED_ADDRESS_STACK_SIZE:
            self.checkedAddresses.pop(-1)
      
    
    def logBlockUpdate(address, wholeBlock=False):
        if wholeBlock:
            _blockUpdates.append(address)
        else:
            _blockBodyUpdates.append(address)
    
    
    def logMutation(address, soft=True):
        _mutationLocations.append(address)
        
        #if(soft):
        #    _blockBodyUpdates.append(address)
        #else:
        #    _blockUpdates.append(address)
            
    
    def clearLogs():
        _mutationLocations.clear()
        _blockBodyUpdates.clear()
        _blockUpdates.clear()
        

class Simulation:
    data = SimulationData()
    
    def cycle(self):
        self.data.clearLogs()
        
        for exeAddr in self.data.executorAddrList:
            self.execute(exeAddr)
            
        for i in range(COSMIC_RAY_MUTATION_ATTEMPT_COUNT):
            if random.random() < COSMIC_RAY_MUTATION_CHANCE:
                index = random.randrange(0, TOTAL_MEM_LEN)
                bit = '0b0' if random.random() < 0.5 else '0b1'
                self.data.soup.overwrite(bit, index)


    def execute(self, executorAddress):    
        executor = utils.readBlock(self.data, executorAddress)
        if executor["header"]["name"] != "executor":
            print("Executor dissappeared at ", executorAddress, " became ", executor)
            self.data.executorAddrList.remove(executorAddress)
            return
        
        blockAddress = executor["body"]
        block = utils.readBlock(self.data, blockAddress)
        
        if block["header"]["execute?"]:
            args = utils.decodeArgs(self.data, blockAddress, block["body"]["arg count"])
            retval = block["body"]["function"](self.data, executorAddress, blockAddress, *args)
            
            if "checked address" in retval:
                addresses = retval["checked address"]
                self.data.addCheckedAddresses(addresses)
            
            # handle executor death, rebirth, and moving
            if "executor init" in retval:
                self.data.executorAddrList.append(retval["executor init"])
                utils.awakenExecutor(self.data, retval["executor init"])
            if "executor deinit" in retval:
                self.data.executorAddrList.remove(retval["executor deinit"])
                utils.killExecutor(self.data, retval["executor deinit"])
                print("Executor went dormant at address ", retval["executor deinit"], " due to instruction ", block)
            if "active executor move" in retval:
                for pair in retval["active executor move"]:
                    self.data.executorAddrList.remove(pair[0])
                    self.data.executorAddrList.append(pair[1])
            
            # instruction pointer updating
            if "jump" in retval:
                blockAddress = retval["jump"]
            elif "skip" in retval:
                blockAddress += 1
                # skip the next retval["skip"] number of non-arg instructions
                while retval["skip"] > 0 and blockAddress < NUM_MEMORY_BLOCKS_IN_SOUP:
                    thisBlock = utils.readBlock(self.data, blockAddress)
                    if thisBlock["header"]["type"] == "instruction":
                        if thisBlock["body"]["type"] != "arg":
                            retval["skip"] -= 1
                    else:
                        retval["skip"] -= 1
                        
                    blockAddress += 1
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

    ancestor = '''T◈▯#####[t1]t3r"04B>$2=13)d^^1(bD^4:4(tT'''#'''T◈▯#####[t]t1r2"23"24B⸘03)c^3(bC$32=)d^^2"23(bD^4:4(tT'''
    sim = Simulation()
    sim.init(ancestor)       
    
    import utils
    exeAddr = sim.data.executorAddrList[0]
    
    #print(''.join(e["header"]["symbol"] for e in [utils.readBlock(sim.data, i) for i in range(0, 500)]))
    
    
    #simString = ''.join(e["header"]["symbol"] for e in [utils.readBlock(sim.data, i) for i in range(0, NUM_MEMORY_BLOCKS_IN_SOUP)])
    #for i in range(CYCLE_COUNT):
    #    sim.cycle()
    #    for update in sim.data._blockUpdates:
    #        simString[update] = utils.readBlock(sim.data, update)["header"]["symbol"]
            
        
    if False:
        print("\n=====ancestor=====")
        pp.pprint(utils.getClaimData(sim.data, exeAddr))
        utils.swapMemoryBlocks(sim.data, exeAddr+1, exeAddr+7)
        
        pp.pprint(utils.getClaimData(sim.data, exeAddr))
        utils.swapMemoryBlocks(sim.data, exeAddr+1, exeAddr+7)
        
        print("Done testing!")
        
    elif False:
        print("\n=====ancestor=====")
        pp.pprint(utils.getClaimData(sim.data, exeAddr))
        
        for i in range(80):
            sim.cycle()
            claimData = utils.getClaimData(sim.data, exeAddr)
            print(claimData["symbols"], "   ", claimData["register values"])
            print(" " * (claimData["executors"][0]["ip"] - claimData["executors"][0]["address"]), "↑")
        
    else:
        
        #print("executor addr: ", exeAddr)
        print("\n=====ancestor=====")
        pp.pprint(utils.getClaimData(sim.data, exeAddr))
        
        # 20 instructions gets us through all of the setup
        for i in range(20):
            sim.cycle()
        
        print("\n=====ancestor=====")
        claimData = utils.getClaimData(sim.data, exeAddr)
        pp.pprint(claimData)
        
        print("\n-------child---------")
        childAddress = claimData["register values"][4]
        pp.pprint(utils.getSymbolRange(sim.data, childAddress, childAddress + len(ancestor)))
        
        # now we're actually doing the copying
        for i in range(1, 5000+1):
            if i % 20 == 0:
                print("=====================Begining cycle num ", i, "=========================")
                print("\n=====ancestor=====")
                pp.pprint(utils.getClaimData(sim.data, exeAddr))
                
                print("\n-------child---------")
                pp.pprint(utils.getSymbolRange(sim.data, childAddress, childAddress + len(ancestor)))
    
            sim.cycle()
        
        print("\n=====ancestor=====")
        pp.pprint(utils.getClaimData(sim.data, exeAddr))
        
        print("\n-------child---------")
        pp.pprint(utils.getSymbolRange(sim.data, childAddress, childAddress + len(ancestor)))
    
        
