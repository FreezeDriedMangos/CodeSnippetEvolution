import const
from const import *
from bitstring import BitArray
from opcode import Opcodes

class SimulationData:
    soup = BitArray('0b' + '0'*TOTAL_MEM_LEN)
    cycle = 0
    blocks = []
    executorAddrList = []
    checkedAddresses = [] # list of tuples (checked, checkedBy)
    
    opcodes = None
    
    _initialized = False;
    
    # recording updates
    _blockBodyUpdates = []
    _blockUpdates = []
    
    _mutationLocations = []
    
    _awakeningLocations = []   # executors activating and deactivating
    _hibernationLocations = []
    
    
    def __init__(self):
        self.opcodes = Opcodes()
    
    
    def initializeBlocks(self):
        bins = list(self.soup.cut(MEM_BLOCK_LEN))
        self.blocks = [self.readBlockFromBits(bits) for bits in bins]
        self._initialized = True
        
    
    def readBlockFromBitsAtAddress(self, addr):
        if addr < 0 or addr >= NUM_MEMORY_BLOCKS_IN_SOUP:
            return None
        
        cut = list(self.soup.cut(MEM_BLOCK_LEN))
        return self.readBlockFromBits(cut[addr])
        
    
    def blockify(self, bitArray):
        cut = list(bitArray.cut(MEM_BLOCK_LEN))
        return [self.readBlockFromBits(bits) for bits in cut]
    
    
    def readBlockFromBits(self, bits):
        block = bits
        block = block.bin
        header = block[0:HEADER_LEN]
        body = block[HEADER_LEN:]
        
        headerInfo = self.opcodes.FLAG_CODES[header].copy()
        try:
            bodyInfo   = headerInfo["interpret body"](self.opcodes, body)
        except:
            print("interpreted something wrong: ", headerInfo)
            print("header was ", header)
            print("block was ", block)
            raise
        
        if headerInfo["symbol"] == None:
            try:
                headerInfo["symbol"] = bodyInfo["symbol"]
            except Exception as e:
                print('Error reading header or body:')
                print(headerInfo)
                print(bodyInfo)
                raise e
            
            
        return {"header": headerInfo, "body": bodyInfo}

    
    
    def addCheckedAddresses(self, addr):
        for a in addr:
            self.checkedAddresses.insert(a, 0)
            
        while len(self.checkedAddresses) >= CHECKED_ADDRESS_STACK_SIZE:
            self.checkedAddresses.pop(-1)
      
    
    def setBlock(self, binary, address):
        assert(type(address) == int)
        assert(type(binary) == str)
        assert(binary[0:1] != '0b')
        assert(len(binary) == MEM_BLOCK_LEN)
        print("setting block ", address, " at index ", MEM_BLOCK_LEN*address)
        
        if random.random() < RANDOMIZE_BLOCK_ON_WRITE_CHANCE:
            binary = ''.join('1' if random.random() < 0.5 else '0' for i in range(MEM_BLOCK_LEN))
            self.logMutation(address, soft=False)
        
        self.soup.overwrite('0b'+binary, MEM_BLOCK_LEN*address)
        self._logBlockUpdate(address, wholeBlock=True)
   
   
    def setBlockBody(self, binary, address):
        assert(type(address) == int)
        assert(type(binary) == str)
        assert(binary[0:1] != '0b')
        assert(len(binary) == BODY_LEN)
        
        self.soup.overwrite('0b'+binary, MEM_BLOCK_LEN*address+HEADER_LEN)
        self._logBlockUpdate(address, wholeBlock=False)
   
    
    def setBlockHeader(self, binary, address):
        assert(type(address) == int)
        assert(type(binary) == str)
        assert(binary[0:1] != '0b')
        assert(len(binary) == HEADER_LEN)
        
        self.soup.overwrite('0b'+binary, MEM_BLOCK_LEN*address)
        self._logBlockUpdate(address, wholeBlock=True)
   
    
    def _logBlockUpdate(self, address, wholeBlock=False):
        if wholeBlock:
            self._blockUpdates.append(address)
        else:
            self._blockBodyUpdates.append(address)
        
        if self._initialized:
            self.blocks[address] = self.readBlockFromBitsAtAddress(address)
            
            if self.blocks[address]["header"]["name"] == "executor":
                self._logExecutorAwakening(address)
            elif self.blocks[address]["header"]["name"] == "dormant executor":
                self._logExecutorHibernation(address)
            
    
    def logMutation(self, address, soft=True):
        self._mutationLocations.append(address)
        
        if self._initialized:
            self.blocks[address] = self.readBlockFromBitsAtAddress(address)
        
            if self.blocks[address]["header"]["name"] == "executor":
                self._logExecutorAwakening(address)
            # we don't want to log a brand new dormant executor as if it were
            # a previously active executor that suddenly
            # went into hibernation
            #elif self.blocks[address]["header"]["name"] == "dormant executor":
                #self._logExecutorHibernation(address)
            
        
    def _logExecutorAwakening(self, addr):
        self._awakeningLocations.append(addr)   # executors activating and deactivating
        
    
    def _logExecutorHibernation(self, addr):
        self._hibernationLocations.append(addr)
        
    
    def clearLogs(self):
        self._mutationLocations.clear()
        self._blockBodyUpdates.clear()
        self._blockUpdates.clear()
        self._awakeningLocations.clear()
        self._hibernationLocations.clear()
        self.cycle += 1
        

from const import COSMIC_RAY_MUTATION_ATTEMPT_COUNT
from const import COSMIC_RAY_MUTATION_CHANCE
from const import TOTAL_MEM_LEN
from const import MEM_BLOCK_LEN
import random
from tracker import Tracker
class Simulation:
    data = SimulationData()
    tracker = None
    
    # WARNING: very slow function
    def symbolString(self):
        import utils
        return ''.join(e["header"]["symbol"] for e in [utils.readBlock(self.data, i) for i in range(0, NUM_MEMORY_BLOCKS_IN_SOUP)])
    
    
    def cycle(self):
        self.data.clearLogs()
        
        for exeAddr in self.data.executorAddrList:
            self.execute(exeAddr)
            
        for i in range(COSMIC_RAY_MUTATION_ATTEMPT_COUNT):
            if random.random() < COSMIC_RAY_MUTATION_CHANCE:
                index = random.randrange(0, TOTAL_MEM_LEN)
                bit = '0b0' if random.random() < 0.5 else '0b1'
                self.data.soup.overwrite(bit, index)
                
                self.data.logMutation(int(index / MEM_BLOCK_LEN), soft=False)
        
        self.tracker.log(self.data)
        

    def execute(self, executorAddress):   
        import utils
        from const import NUM_MEMORY_BLOCKS_IN_SOUP
        from const import MEM_BLOCK_LEN
        
        executor = utils.readBlock(self.data, executorAddress)
        if executor["header"]["name"] != "executor":
            print("Executor dissappeared at ", executorAddress, " became ", executor)
            self.data.executorAddrList.remove(executorAddress)
            return
        
        blockAddress = executor["body"]
        try:
            block = utils.readBlock(self.data, blockAddress)
        except:
            cut = [sim.data.soup.cut(MEM_BLOCK_LEN)]
            print("attempted read at ", blockAddress, " of ", cut[blockAddress])
            print("surrounding bits:", cut[blockAddress-1:blockAddress+1])
            raise
        
        printArgs = ["running instruction ", block["header"]["symbol"], " @ ", blockAddress]
        bef = blockAddress
            
        if block["header"]["execute?"]:
            args = utils.decodeArgs(self.data, blockAddress, block["body"]["arg count"])
            printArgs.extend(["function: ", block["body"]["function"], " with args ", args])
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
            
            #utils.registerWrite(self.data, executorAddress, executorAddress, blockAddress, unsigned=True)
            
        elif block["header"]["type"] == "register":
            utils.registerWrite(self.data, executorAddress, blockAddress, 0)
            #utils.registerWrite(self.data, executorAddress, executorAddress, blockAddress+1)
            blockAddress+=1
        else:
            #utils.registerWrite(self.data, executorAddress, executorAddress, blockAddress+1)
            blockAddress+=1
            
        #print("\tsetting ip from ", bef, " to ", blockAddress)
        utils.registerWrite(self.data, executorAddress, executorAddress, blockAddress, unsigned=True)
        print(*printArgs)
        
    
    def init(self, ancestorString):
        import random
        import compiler
        import utils
        
        # put a random memory block at each location
        for i in range(0, TOTAL_MEM_LEN, MEM_BLOCK_LEN):
            self.data.soup.overwrite('0b'+random.choice(self.data.opcodes.SPAWN_LIST), i)  
        
        # interpret the ancestor string
        ancestor = compiler.compileGenome(ancestorString)
        ancestorData = BitArray('0b' + ancestor)
        
        ancestorBlocks = self.data.blockify(ancestorData) #[utils.readBlock(ancestorData, i) for i in range(len(ancestorString))]
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
        
        
        # initialize the data
        self.data.initializeBlocks()
        
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
    
        
