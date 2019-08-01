from sim import Simulation
import utils
import tkinter as tk

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


chunkSize = 50
ancestor = '''T◈▯#####[t1]t3r"04B>$2=13)d^^1(bD^4:4(tT''' #'''T◈▯###''' '''##[t]t1r2"23"24B⸘03)c^3(bC$32=)d^^2"23(bD^4:4(tT'''

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

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()


    def callback(self):
        self.running = False
        sim.forceQuit()


    def run(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        
        self.cycleLabel = tk.Label(self.root, text="Cycle Num -1")
        self.cycleLabel.pack()
        CreateToolTip(self.cycleLabel, waittime=0, getText=lambda:"test")
                
        
        self.label = tk.Label(self.root, text="Loading, Step 1...")
        self.label.pack()

        self.gridFrame = tk.Frame(self.root, bg="#202020", highlightthickness=10)

        #button = tk.Button(self.root, text='-')
        
        self.initialized = True
        self.root.mainloop()
    
    
    # I didn't want this to be its own function, but Python is super
    # funky with variable scope. When I had this in the inner for loop of initGrid()
    # every label's tooltip would be initialized as if it were the last one
    # ie, it would use the last-set value of l, r, and c
    # now that it's its own function, it works
    def __makeLabel(self, r, c, simString):
        l = tk.Label(self.gridFrame, text=simString[r][c], font='TkFixedFont', highlightthickness=0, bg=COLORS["background"], fg=COLORS["foreground"])
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
        self.gridFrame.pack()
        self.baseColors = [COLORS["background"]] * len(self.linearGrid)
    
    
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
       
       
sim.init(ancestor)
simString = [c for c in sim.symbolString()]

app.initGrid(unjoinedLineBreak(simString))



import utils
import colorsys
from frontend_colors import colorLerp

updateFade = {}
def setFadeFrom(index, tocolor, fromcolor):
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
        updateFade[index] = (decay-0.01, updateColor, )
        
    for key in removeKeys:
        updateFade.pop(key)
    

 
app.root.quit()
print("Application has quit!")       
        
        
        
        
        
        
