from sim import Simulation
import utils
import tkinter as tk


chunkSize = 50

ancestor = '''T◈▯#####[t1]t3r"04B>$2=13)d^^1(bD^4:4(tT''' #'''T◈▯###''' '''##[t]t1r2"23"24B⸘03)c^3(bC$32=)d^^2"23(bD^4:4(tT'''

sim = Simulation()
      
 

 

#
# Below class modified from https://stackoverflow.com/a/1835036
#
import threading

class App(threading.Thread):

    grid = []
    linearGrid = []
    gridWidth = 0

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()


    def callback(self):
        self.root.quit()


    def run(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        
        self.cycleLabel = tk.Label(self.root, text="Cycle Num -1")
        self.cycleLabel.pack()
        
        self.label = tk.Label(self.root, text="Loading, Step 1...")
        self.label.pack()

        self.gridFrame = tk.Frame(self.root)

        #button = tk.Button(self.root, text='-')
        
        self.initialized = True
        self.root.mainloop()
        
    
    def initGrid(self, simString):
        self.gridWidth = len(simString[0])
        for r in range(len(simString)):
            row = []
            for c in range(len(simString[r])):
                l = tk.Label(self.gridFrame, text=simString[r][c], font='TkFixedFont', highlightthickness=0)
                l.grid(column=c, row=r)
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
    app.setBackground(i, "#8cdba1")
    

app.label.config(text="Running Sim")

for i in range(100):
    app.cycleLabel.config(text="Cycle Num " + str(i))
    
    sim.cycle()
    for update in sim.data._blockUpdates:
        simString[update] = utils.readBlock(sim.data, update)["header"]["symbol"]
        app.setBackground(update, "#fff385")
        app.setGridText(update, simString[update])
    

        
        
        
        
        
        
        
