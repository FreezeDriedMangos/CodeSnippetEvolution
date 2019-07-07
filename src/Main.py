INSTRUCTION_LENGTH = 4
NUM_INSTRUCTIONS_IN_SOUP = 10000

class Simulation:
    soup = " " * INSTRUCTION_LENGTH * NUM_INSTRUCTIONS_IN_SOUP
    instructionPointers = [] # each one executes code!
    
    
    def run():
        while(True):
            
            
    def execute(soup):
        instruction = soup[ip:ip+INSTRUCTION_LENGTH]
        instructionCode = instruction[0]
        argDecodeKeys = INSTRUCTIONS[instructionCode][1]
        
        args = instruction[1:4]
        
        for i in range(3):
            decodeKey = argDecodeKeys[i]
        
            if decodeKey == 'i' or decodeKey == '_':
                # do nothing
            elif decodeKey == 'b':
                args[i] = -int(args[i])
            elif decodeKey == 'f' or argDecodeKeys[i] == 'n':
                args[i] = int(args[i])
            elif decodeKey == '0':
                args[i] = args[0]
            elif decodeKey == '1':
                args[i] = args[1]
            elif decodeKey == '2':
                args[i] = args[1]
            elif decodeKey == '+': # combine the remaining digits into one number
            elif decodeKey == '-': # combine the remaining digits into one negative number
                
        function = INSTRUCTIONS[instructionCode][0]
        ip += INSTRUCTION_LENGTH * function(*args)
            
                
        

