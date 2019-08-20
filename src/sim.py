import const
from const import *
from bitstring import BitArray
from opcode import Opcodes
import random

class SimulationData:
    cycle = 0
    blocks = []
    executorAddrList = []
    checkedAddresses = [] # list of tuples (checked, checkedBy)
    spawnTable = []
    _maxRandVal = 0
    
    opcodes = None
    
    _initialized = False
    
    # recording updates
    _blockBodyUpdates = []
    _blockUpdates = []
    
    _mutationLocations = []
    
    _awakeningLocations = []   # executors activating and deactivating
    _hibernationLocations = []
    _dissapearanceLocations = []
    
    
    def __init__(self, spawnTable):
        self.opcodes = Opcodes()
        self.spawnTable = spawnTable
        
        if self.spawnTable == None:
            self.spawnTable = [(1, symbol) for symbol in self.opcodes._SYMBOL_DICTIONARY if self.opcodes._SYMBOL_DICTIONARY[symbol]["header"]["spawnable?"]]
        
        self._maxRandVal = sum(e[0] for e in self.spawnTable)-1
        
        expectedDistribution = {a[1]: a[0]/self._maxRandVal for a in self.spawnTable}
        distribution = {a[1]: 0 for a in self.spawnTable}
        # put a random memory block at each location
        for i in range(0, NUM_MEMORY_BLOCKS_IN_SOUP):
            self.blocks.append(self.spawnRandomBlock())
            distribution[self.blocks[-1]["header"]['symbol']] += 1
        
        distribution = {s: distribution[s]/len(self.blocks) for s in distribution}
        print("symbol\tspawn chance\tactual distribution (all in percentage)")
        for symbol in distribution:
            print(symbol, "\t", round(100*expectedDistribution[symbol], 2), "\t", round(100*distribution[symbol], 2))
        print("Total error: ", sum(abs(expectedDistribution[s] - distribution[s]) for s in distribution))
        
        self._initialized = True
        
    
    def getRandomSymbol(self):
        initVal = randval = random.randint(0, self._maxRandVal)
        j = -1
        while randval >= 0 and j < len(self.spawnTable):
            j += 1
            randval -= self.spawnTable[j][0]
        
        if randval > 0 or j >= len(self.spawnTable):
            print("FAILURE in SimulationData.getRandomSymbol()")
            import pprint
            p = pprint.PrettyPrinter(indent=4)
            p.pprint(self.spawnTable)
            print("weights sum = ", sum(e[0] for e in self.spawnTable))
            print("rand value = ", initVal)
            print("after processing = ", randval)
            raise
            
        return self.spawnTable[j][1]
   
   
    def spawnRandomBlock(self):
        symbol = self.getRandomSymbol()
        return self.opcodes.fetchBlock(symbol)
   
    
    def addCheckedAddress(self, pair):
        self.checkedAddresses.insert(0, pair)
            
        while len(self.checkedAddresses) >= CHECKED_ADDRESS_STACK_SIZE:
            self.checkedAddresses.pop(-1)
      
    
    def setBlock(self, newBlock, address):
        assert(type(address) == int)
        assert(type(newBlock) == dict)
        assert("body" in newBlock)
        assert("header" in newBlock)
        
        #print("setting block ", address, " at index ", MEM_BLOCK_LEN*address)
        
        if random.random() < RANDOMIZE_BLOCK_ON_WRITE_CHANCE:
            newBlock = self.spawnRandomBlock()
            self.logMutation(address, soft=False)
        
        self.blocks[address] = newBlock
        self._logBlockUpdate(address, wholeBlock=True)
   
   
    def setBlockBody(self, content, address):
        assert(type(address) == int)
        bodyType = type(self.blocks[address]["body"])
        assert(type(content) == int or type(content) == type(None))
        assert(bodyType == int or bodyType == type(None))
        
        self.blocks[address]["body"] = content
        self._logBlockUpdate(address, wholeBlock=False)
   
    
    def _logBlockUpdate(self, address, wholeBlock=False):
        if wholeBlock:
            self._blockUpdates.append(address)
        else:
            self._blockBodyUpdates.append(address)
        
        if self._initialized and wholeBlock:
            if self.blocks[address]["header"]["name"] == "executor":
                self._logExecutorAwakening(address)
            elif self.blocks[address]["header"]["name"] == "dormant executor":
                self._logExecutorHibernation(address)
            elif address in self.executorAddrList and self.blocks[address]["header"]["type"] != "executor":
                self._logExecutorDissapearance(address)
            
    
    def logMutation(self, address, soft=True):
        self._mutationLocations.append(address)
        
        if self._initialized:
            self.blocks[address] = self.readBlockFromBitsAtAddress(address)
        
            #if self.blocks[address]["header"]["name"] == "executor":
                #self._logExecutorAwakening(address)
            ## we don't want to log a brand new dormant executor as if it were
            ## a previously active executor that suddenly
            ## went into hibernation
            ##elif self.blocks[address]["header"]["name"] == "dormant executor":
                ##self._logExecutorHibernation(address)
            
        
    def _logExecutorAwakening(self, addr):
        self._awakeningLocations.append(addr) 
        
    
    def _logExecutorHibernation(self, addr):
        self._hibernationLocations.append(addr)
        
    
    def _logExecutorDissapearance(self, addr):
        self._dissapearanceLocations.append(addr)
    
    
    def clearLogs(self):
        self._mutationLocations.clear()
        self._blockBodyUpdates.clear()
        self._blockUpdates.clear()
        self._awakeningLocations.clear()
        self._hibernationLocations.clear()
        self._dissapearanceLocations.clear()
        self.cycle += 1
        

import random
from tracker import Tracker
import utils
from const import NUM_MEMORY_BLOCKS_IN_SOUP
    
class Simulation:
    data = None
    tracker = None
    
    def symbolString(self):
        return ''.join(e["header"]["symbol"] for e in [utils.readBlock(self.data, i) for i in range(0, NUM_MEMORY_BLOCKS_IN_SOUP)])
    
    
    def cycle(self):
        self.data.clearLogs()
        
        removeList = []
        for exeAddr in self.data.executorAddrList:
            try:
                self.execute(exeAddr)
            except Exception as e:
                print("\n\n\n")
                print("Executor at ", exeAddr, " had a serious error, resulting in it going into dormancy:")
                print(e)
                insAddr = self.data.blocks[exeAddr]["body"]
                if type(insAddr) == int:
                    print("Cause: ", self.data.blocks[insAddr]["header"]["symbol"])
                    print("surrounding symbols: ", "@" + ''.join(self.data.blocks[i]["header"]["symbol"] for i in range(insAddr-4, insAddr+5)) + "@")
                else:
                    print("Cause: symbol at ", exeAddr, " is not an executor or has an improper body: ")
                    print(self.data.blocks[exeAddr])
                print("exception stack trace:")
                import traceback
                traceback.print_exc()
                print("\n\n\n")
                utils.killExecutor(self.data, exeAddr)
                removeList.append(exeAddr)
                raise
        for e in removeList:
            if e in self.data.executorAddrList:
                self.data.executorAddrList.remove(e)
        
        self.tracker.log(self.data)
        

    def execute(self, executorAddress):   
        executor = self.data.blocks[executorAddress]
        if executor["header"]["name"] != "executor":
            print("Executor dissappeared at ", executorAddress, " became ", executor)
            raise Exception("Called execute on something other than an executor: " + executor["header"]["symbol"] + "@" + str(executorAddress))
        
        blockAddress = executor["body"]
        try:
            block = self.data.blocks[blockAddress]
        except:
            print("failed attempted read at ", blockAddress, " of ", self.data.blocks)
            raise
        
        printArgs = ["running instruction ", block["header"]["symbol"], " @ ", blockAddress]
        bef = blockAddress
            
        if block["header"]["execute?"]:
            args = utils.decodeArgs(self.data, blockAddress, block["body"]["arg count"])
            printArgs.extend(["function: ", block["body"]["function"], " with args ", args])
            retval = block["body"]["function"](self.data, executorAddress, blockAddress, *args)
            
            if "checked address" in retval:
                addresses = retval["checked address"]
                self.data.addCheckedAddress(addresses)
            
            # handle executor death, rebirth, and moving
            if "executor init" in retval:
                self.data.executorAddrList.append(retval["executor init"])
                utils.awakenExecutor(self.data, retval["executor init"])
            if "executor deinit" in retval:
                self.data.executorAddrList.remove(retval["executor deinit"])
                try:
                    utils.killExecutor(self.data, retval["executor deinit"])
                except:
                    print("weird funky stuff happened while attempting executor hibernation")
                    print("Executor went dormant at address ", retval["executor deinit"], " due to instruction ", block)
                    raise
                    
                print("Executor went dormant at address ", retval["executor deinit"], " due to instruction ", block["header"]["symbol"])
                if "details" in retval:
                    print("\t", retval["details"])
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
            
            
        elif block["header"]["type"] == "register":
            utils.registerWrite(self.data, executorAddress, blockAddress, 0)
            blockAddress+=1
        else:
            blockAddress+=1
            
        #print("\tsetting ip from ", bef, " to ", blockAddress)
        if self.data.blocks[executorAddress]["header"]["name"] == "executor":
            # if this executor is still there and still alive
            utils.registerWrite(self.data, executorAddress, executorAddress, blockAddress)
        #print(*printArgs)
        return True
   
   
    def spawnCreature(self, creatureString):
        # interpret the ancestor string
        creatureBlocks = [self.data.opcodes.fetchBlock(s) for s in creatureString]
        creatureExecutorLocs = [i for i in range(len(creatureBlocks)) if creatureBlocks[i]["header"]["name"] == "executor"]
        
        # seed the soup with one common ancestor
        creatureLoc = random.randrange(0, NUM_MEMORY_BLOCKS_IN_SOUP-len(creatureString))
        self.data.blocks[creatureLoc:len(creatureString)] = creatureBlocks
        
        # find ancestor's executor
        for loc in creatureExecutorLocs:
            loc = loc + creatureLoc
            self.data.executorAddrList.append(loc)
            
            # initialize this executor
            utils.registerWriteIgnoreDumpMechanics(self.data, loc, loc)
        
   
    
    def init(self, ancestorString, spawnTable=None):
        self.data = SimulationData(spawnTable)
        
        # seed the soup with life
        self.spawnCreature(ancestorString)
        
        # initialize the tracker
        self.tracker = Tracker(self.data)
     
     
    def forceQuit(self):
        print("Saving...")
        self.tracker._writeLogs()
        print("\tDone!")
        

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
    
        
