from sim import Simulation
import utils
import tkinter as tk


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

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()


    def callback(self):
        self.running = False
        self.root.quit()


    def run(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        
        self.cycleLabel = tk.Label(self.root, text="Cycle Num -1")
        self.cycleLabel.pack()
        CreateToolTip(self.cycleLabel, waittime=0, getText=lambda:"test")
                
        
        self.label = tk.Label(self.root, text="Loading, Step 1...")
        self.label.pack()

        self.gridFrame = tk.Frame(self.root, bg="#202020")

        #button = tk.Button(self.root, text='-')
        
        self.initialized = True
        self.root.mainloop()
    
    
    # I didn't want this to be its own function, but Python is super
    # funky with variable scope. When I had this in the inner for loop of initGrid()
    # every label's tooltip would be initialized as if it were the last one
    # ie, it would use the last-set value of l, r, and c
    # now that it's its own function, it works
    def __makeLabel(self, r, c, simString):
        l = tk.Label(self.gridFrame, text=simString[r][c], font='TkFixedFont', highlightthickness=0, bg="#202020", fg="#aaaaaa")
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
    
    
    def setBackground(self, index, color):
        #row = int(index / self.gridWidth)
        #column = index % self.gridWidth
        #self.grid[row][column].config(bg=color)
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
ancestor = utils.getClaimBoundaries(sim.data, sim.data.executorAddrList[0])
for i in range(ancestor[0], ancestor[1]+1):
    app.setBackground(i, "#0d5922")
    

app.label.config(text="Running Sim")
print(sim.data.executorAddrList, " EXECTUTORS ")


updateFade = {}

import colorsys
BLOCK_UPDATE_COLOR = colorsys.rgb_to_hsv(99/255, 105/255, 2/255)
BLOCK_UPDATE_SATURATION = BLOCK_UPDATE_COLOR[1]

def rgbToHex(r, g, b):
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    
    r = hex(r)[2:]
    r = r if len(r) > 1 else "0"+r
    
    g = hex(g)[2:]
    g = g if len(g) > 1 else "0"+g
    
    b = hex(b)[2:]
    b = b if len(b) > 1 else "0"+b
    
    return "#"+r+g+b


# run the simulation
i = 0
while app.running:
    i += 1
    app.cycleLabel.config(text="Cycle Num " + str(i))
    
    # update
    sim.cycle()
    
    # record blocks that have been updated
    for update in sim.data._blockUpdates:
        simString[update] = utils.readBlock(sim.data, update)["header"]["symbol"]
        app.setGridText(update, simString[update])
        updateFade.update({update: BLOCK_UPDATE_SATURATION})
    
    removeKeys = []
    # update colors
    for key in updateFade:
        saturation = updateFade[key]
        
        color = colorsys.hsv_to_rgb(BLOCK_UPDATE_COLOR[0], saturation, BLOCK_UPDATE_COLOR[2])
        
        app.setBackground(update, rgbToHex(*color))
        updateFade[key] -= 0.01
        
        if updateFade[key] <= 0:
            #updateFade.pop(key)
            app.setBackground(update, rgbToHex(0,0,0))
            removeKeys.append(key)
    
    for key in removeKeys:
        updateFade.pop(key)
    

        
        
        
        
        
        
        
