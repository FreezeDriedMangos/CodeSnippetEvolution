
import re
import opcode
import util

def compile(genomeString):
        codeType = genomeString[0:4] 
        genomeString = genomeString[4:]
        
        if codeType is "SYMB":
            genomeString = re.sub(r"(\/\/ .*\n)|(\/\/ .*)| |\n", "", genomeString)
            
            
            
def symbolAssembly():
    instructionCode = [key for key in FLAG_CODES if FLAG_CODES[key]["type"] is "instruction"][0]
    
    specialSymbols = {FLAG_CODES[key]["symbol"]: key + FLAG_CODES[key]["defaultBody"] for key in FLAG_CODES if FLAG_CODES[key]["symbol"] is not None}
    instructionSymbols = {INSTRUCTIONS[i]["symbol"]: instructionCode + utils.intToBinary(i, BODY_LEN, unsigned=true) for i in range(len(INSTRUCTIONS))}
    
    symbols = specialSymbols
    symbols.update(instructionSymbols)
    return symbols
    
    
    
print(symbolAssembly())
