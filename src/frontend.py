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
        self.root = tkinter.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)

        label = tk.Label(self.root, text="Hello World")
        label.pack()

        button = tkinter.Button(self.root, text='-')

        self.root.mainloop()


app = App()
print('Now we can continue running code while mainloop runs!')

for i in range(100):
    print(i)
