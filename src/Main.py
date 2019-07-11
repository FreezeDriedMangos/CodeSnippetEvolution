import random
from opcode import *


INSTRUCTION_LENGTH = 4
NUM_INSTRUCTIONS_IN_SOUP = 10000

class Simulation:
    soup = " " * INSTRUCTION_LENGTH * NUM_INSTRUCTIONS_IN_SOUP
    ats = [] # each one executes code!
    
    
    def run(self):
        self.initialize()
        for i in range(20):
            for at in self.ats:
                ip = self.execute(at.index + int(self.soup[at.index+1:at.index+INSTRUCTION_LENGTH]))
                ip += int(self.soup[at.index+1:at.index+4])
                self.soup[at.index+1:at.index+4] = str.format(ip, '03d')
            self.display()
        
        
    def display(self, wrapLen=64):
        print('->\n'+'\n'.join([self.soup[i:i+wrapLen] for i in range(0, len(self.soup), wrapLen)]))
        
            
    def initialize(self):
        instr = set(key for key in INSTRUCTIONS)
        for i in range(len(self.soup), INSTRUCTION_LENGTH):
            if self.soup[i] == ' ':
                self.soup[i] = random.choice(instr)
                self.soup[i+1:i+INSTRUCTION_LENGTH] = [""+random.randint(0,9) for j in range(INSTRUCTION_LENGTH-1)]
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
