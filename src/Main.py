import random
from opcode import *

INSTRUCTION_LENGTH = 4
NUM_INSTRUCTIONS_IN_SOUP = 10

class Simulation:
    soup = []
    ats = [] # each one executes code!
        
    def __init__(self, s=None):
        if s is not None:
            import re
            s = re.sub(r'(\d+)', r'\1_', s)
            s = re.sub(r'(\d)',  r'_\1', s)
            s = re.split(r'_', s)
            del s[-1]
            self.soup = s
        else:
            self.soup = ["_"] * INSTRUCTION_LENGTH * NUM_INSTRUCTIONS_IN_SOUP
            self.initialize()
        
    
    def run(self):
        for i in range(20):
            for at in self.ats:
                ip = self.execute(at.index + int(self.soup[at.index+1:at.index+INSTRUCTION_LENGTH]))
                ip += int(self.soup[at.index+1:at.index+4])
                self.soup[at.index+1:at.index+4] = str.format(ip, '03d')
            self.display()
        
        
    def display(self, wrapLen=64, full=False):
        if not full:
            soupDisp = ''.join(self.soup[i] for i in range(0, len(self.soup), INSTRUCTION_LENGTH))
        else:
            soupDisp = ''.join(self.soup)
        print('\n'.join([soupDisp[i:i+wrapLen] for i in range(0, len(soupDisp), wrapLen)]))
            
        
            
    def initialize(self):
        instr = list(key for key in INSTRUCTIONS)
        for i in range(0, len(self.soup), INSTRUCTION_LENGTH):
            if self.soup[i] == '_':
                self.soup[i] = random.choice(instr)
                self.soup[i+1:i+INSTRUCTION_LENGTH] = [str(random.randint(0,9)) for j in range(INSTRUCTION_LENGTH-1)]
            if self.soup[i] == '@':
                self.ats.append(At(i))
        
            
    def execute(self, ip, at):
        instruction = self.soup[ip:ip+INSTRUCTION_LENGTH]
        instructionCode = instruction[0]
        argDecodeKeys = INSTRUCTIONS[instructionCode][1]
        
        args = instruction[1:4]
        
        for i in range(3):
            decodeKey = argDecodeKeys[i]
        
            if decodeKey == 'i' or decodeKey == '_':
                # do nothing
                _ignore_me_ = 0
            elif decodeKey == 'b':
                args[i] = -int(args[i])
            elif decodeKey == 'r':
                args[i] = 'r'+args[i]
            elif decodeKey == '0':
                args[i] = args[0]
            elif decodeKey == '1':
                args[i] = args[1]
            elif decodeKey == '2':
                args[i] = args[1]
            elif decodeKey == '+':  # combine the remaining digits into one number
                args[i] = int(''.join(args[i:]))
            elif decodeKey == '-':  # combine the remaining digits into one negative number
                args[i] = -int(''.join(args[i:]))

        function = INSTRUCTIONS[instructionCode][0]
        return INSTRUCTION_LENGTH * function(*args, at, self.soup, ip)
            
                
class At:
    index = 0
    registers = [0]*11 # registers[10] is the dump register
    foundStacks = {key : -1 for key in INSTRUCTIONS}

    def __init__(self, i):
        self.index = i
        self.registers[10] = 1000
        
        
        
        
if __name__ == "__main__":   
    sim = Simulation(None)
    sim.display()
    sim.display(full=True)
    #sim.run()
        
        
        
        
