from sim import Simulation
import utils
import tkinter as tk


chunkSize = 50

ancestor = '''T◈▯#####[t1]t3r"04B>$2=13)d^^1(bD^4:4(tT'''#'''T◈▯#####[t]t1r2"23"24B⸘03)c^3(bC$32=)d^^2"23(bD^4:4(tT'''

sim = Simulation()
      
 

 

#
# Below class modified from https://stackoverflow.com/a/1835036
#
import threading

class App(threading.Thread):

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

        #button = tk.Button(self.root, text='-')
        
        self.initialized = True
        self.root.mainloop()
        

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

        
sim.init(ancestor)
simString = [c for c in sim.symbolString()]
app.label.config(text=lineBreak(simString))
print("Begining sim")

for i in range(100):
    app.cycleLabel.config(text="Cycle Num " + str(i))
    
    sim.cycle()
    for update in sim.data._blockUpdates:
        simString[update] = utils.readBlock(sim.data, update)["header"]["symbol"]
    
    if len(sim.data._blockUpdates) > 0:
        app.label.config(text=lineBreak(simString))
        print("UPDATE")

        
        
        
        
        
        
        
