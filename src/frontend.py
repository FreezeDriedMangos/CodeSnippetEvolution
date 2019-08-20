from sim import Simulation
import utils
import tkinter as tk
from compiler import genomeSymbolsFromFile
from compiler import readSpawnTableFromFile
from frontend_colors import COLORS


BLOCK_BODY_TOOLTIP_LIST = ["executor", "register", "dump register"]
def getTooltipText(simData, index, text):
    retval = "index " + str(index) + " " + text
   
    block = utils.readBlock(simData, index)
    if block is None:
        print("Block was none at index ", index)
    
    blockType = block["header"]["type"]
    
    if blockType not in BLOCK_BODY_TOOLTIP_LIST:
        return retval
    return retval + str(block["body"])


MAX_INSTRUCTION_LIST_SIZE = 10
UPDATE_COLOR_DECAY_SPEED = 0.01#0.0015


chunkSize = 50
ancestor = genomeSymbolsFromFile("genomes/anc1_1.gne")
spawnTable = readSpawnTableFromFile("spawnTables/spawnTable1.spt")

sim = Simulation()
 

#
# Below class modified from https://stackoverflow.com/a/1835036
#
import threading
from tkTooltip import CreateToolTip

class App(threading.Thread):
    grid = []
    linearGrid = []
    gridWidth = 0
    running = True
    baseColors = []
    executorPanels = {}

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()


    def callback(self):
        self.running = False
        sim.forceQuit()


    def run(self):
        self.root = tk.Tk()
        self.root.title("Virus Evolution Proof of Concept")
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        
        # main window
        self.cycleLabel = tk.Label(self.root, text="Cycle Num -1")
        self.cycleLabel.pack()
        
        self.label = tk.Label(self.root, text="Loading, Step 1...")
        self.label.pack()
        
        self.soupView = tk.Frame(self.root, bg="#202020", highlightthickness=10)
        
        # second window
        self.executorWindow = tk.Toplevel(self.root)
        self.executorView = tk.Frame(self.executorWindow, bg="green")
        self.executorView.pack(fill=tk.X)
        tk.Label(self.executorView, text="EXECUTORS").pack()
        
        # finalize
        self.initialized = True
        self.root.mainloop()
    
    
    # I didn't want this to be its own function, but Python is super
    # funky with variable scope. When I had this in the inner for loop of initGrid()
    # every label's tooltip would be initialized as if it were the last one
    # ie, it would use the last-set value of l, r, and c
    # now that it's its own function, it works
    def __makeLabel(self, r, c, simString):
        l = tk.Label(self.soupView, text=simString[r][c], font='TkFixedFont', highlightthickness=0, bg=COLORS["background"], fg=COLORS["foreground"])
        l.grid(column=c, row=r)
        
        CreateToolTip(l, waittime=0, getText=lambda:getTooltipText(sim.data, r*self.gridWidth + c, l["text"]))
        return l
    
    
    def initGrid(self, simString):
        self.gridWidth = len(simString[0])
        for r in range(len(simString)):
            row = []
            for c in range(len(simString[r])):
                l = self.__makeLabel(r, c, simString)
                row.append(l)
                self.linearGrid.append(l)
                
            self.grid.append(row)
        self.soupView.pack()
        self.baseColors = [COLORS["background"]] * len(self.linearGrid)
    
    
    def makeExecutorPanel(self, sim, executorLoc):
        executor = utils.readBlock(sim.data, executorLoc)
        
        panel = tk.Frame(self.executorView, borderwidth=1)
        title = tk.Label(panel, text="Executor @"+str(executorLoc))
        ip = tk.Label(panel, text="->"+str(executor["body"])+"<-")
        instructionList = tk.Label(panel, text=" ")
        
        title.pack()
        ip.pack()
        instructionList.pack()
        panel.pack(side=tk.LEFT)
        
        self.executorPanels.update({executorLoc: [panel, title, ip, [], instructionList]})
    
    
    def updateExecutorPanel(self, sim, executorLoc):
        if executorLoc not in self.executorPanels:
            self.makeExecutorPanel(sim, executorLoc)
        
        executor = utils.readBlock(sim.data, executorLoc)
        display = self.executorPanels[executorLoc]
        display[2].config(text="->"+str(executor["body"])+"<-")
        
        nextInst = utils.readBlock(sim.data, executor["body"])
        display[3].insert(0, nextInst["header"]["symbol"])
        
        while len(display[3]) > MAX_INSTRUCTION_LIST_SIZE:
            display[3].pop()
        
        display[4].config(text="\n".join(display[3]))
        
    
    def setBaseBackground(self, index, color):
        self.linearGrid[index].config(bg=color)
        self.baseColors[index] = color
    
    
    def setBackground(self, index, color):
        self.linearGrid[index].config(bg=color)
    
    
    def setGridText(self, index, text):
        self.linearGrid[index].config(text=text)
        

app = App()
print('Now we can continue running code while mainloop runs!')

# wait for the window to initialize
while True:
    try:
        assert(app.initialized)
    except:
        continue
    break


app.label.config(text="Loading, Step 2...")


def lineBreak(simString, lineLen=80):
    return '\n'.join([''.join(simString[i:i+lineLen]) for i in range(0, len(simString), lineLen)])


def unjoinedLineBreak(simString, lineLen=80):
    return [simString[i:i+lineLen] for i in range(0, len(simString), lineLen)]
       
       
sim.init(ancestor, spawnTable)
simString = [c for c in sim.symbolString()]

app.initGrid(unjoinedLineBreak(simString))

for loc in sim.data.executorAddrList:
    app.makeExecutorPanel(sim, loc)
print(app.executorPanels)

import utils
import colorsys
from frontend_colors import colorLerp

updateFade = {}
def setFadeFrom(index, tocolor, fromcolor):
    if i < 0 or i >= len(app.baseColors):
        return
    app.baseColors[i] = tocolor
    updateFade.update({i: (1, fromcolor)})
    

ancestor = utils.getClaimBoundaries(sim.data, sim.data.executorAddrList[0])
for i in range(ancestor[0], ancestor[1]+1):
    app.setBaseBackground(i, COLORS["life"])
    
    

app.label.config(text="Running Sim")
print(sim.data.executorAddrList, " EXECTUTORS ")


# run the simulation
i = 0
while app.running:
    i += 1
    app.cycleLabel.config(text="Cycle Num " + str(i))
    
    # update executor panels
    for loc in sim.data.executorAddrList:
        app.updateExecutorPanel(sim, loc)
    
    # logic update
    sim.cycle()
    
    # record blocks that have been updated
    for update in sim.data._blockUpdates:
        simString[update] = utils.readBlock(sim.data, update)["header"]["symbol"]
        app.setGridText(update, simString[update])
        updateFade.update({update: (1, COLORS["block update"])})
    
    # update any executor awakenings or hibernations
    for hibernation in sim.data._hibernationLocations:
        claim = utils.getClaimData(sim.data, hibernation)
        exe = [e for e in claim["executors"] if e["active"]]
        
        if len(exe) == 0:
            for i in range(*claim["range bounds"]):
                #app.baseColors[i] = COLORS["background"]
                #updateFade.update({i: (1, COLORS["life"])})
                try:
                    setFadeFrom(i, COLORS["background"], app.baseColors[i])
                except:
                    print("Encountered error setting fade for index ", i)
    
    for awakening in sim.data._awakeningLocations:
        claim = utils.getClaimData(sim.data, awakening)
        print("\n===============================\ntrying to set color for awakening claim ", claim["range bounds"])
        for i in range(*claim["range bounds"]):
            #app.baseColors[i] = COLORS["life"]
            #updateFade.update({i: (1, COLORS["background"])})
            setFadeFrom(i, COLORS["life"], app.baseColors[i])
    
    
    # update color fading
    removeKeys = []
    for index in updateFade:
        baseColor = app.baseColors[index]
        decay, updateColor = updateFade[index]
        
        if decay <= 0:
            app.setBackground(index, baseColor)
            removeKeys.append(index)
            continue
        
        color = colorLerp(baseColor, updateColor, decay)
        app.setBackground(index, color)
        updateFade[index] = (decay-UPDATE_COLOR_DECAY_SPEED, updateColor, )
        
    for key in removeKeys:
        updateFade.pop(key)
    

 
app.root.quit()
print("Application has quit!")       
        
        
        
        
        
        
