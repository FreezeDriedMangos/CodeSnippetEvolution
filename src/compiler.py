
import re
import opcode
from opcode import *
import utils

def compileGenomeFromFile(filepath):
    genomeString = open(genomeString, 'r').read()
    
    genomeString = re.sub(r"(\/\/ .*\n)|(\/\/ .*)| |\n", "", genomeString)
    
    return (compileGenome(genomeString), genomeString)


def compileGenome(genomeString):
    assemb = symbolAssembly()
    assembledGenome = "".join(assemb[symbol] for symbol in genomeString)
    return assembledGenome
    
            
def symbolAssembly():
    instructionCode = [key for key in FLAG_CODES if FLAG_CODES[key]["type"] == "instruction"][0]
    
    specialSymbols = {FLAG_CODES[key]["symbol"]: key + FLAG_CODES[key]["default body"] for key in FLAG_CODES if FLAG_CODES[key]["symbol"] != None}
    instructionSymbols = {INSTRUCTIONS[i]["symbol"]: instructionCode + utils.intToBinary(i, BODY_LEN, unsigned=True) for i in range(len(INSTRUCTIONS))}
    
    symbols = specialSymbols
    symbols.update(instructionSymbols)
    return symbols
    

if __name__ == "__main__":    
    import pprint  
    pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(symbolAssembly())
    #pp.pprint(INSTRUCTIONS)

    from bitstring import BitArray
    comp, genome = compileGenomeFromFile("genome.anc")
    comp = BitArray("0b"+comp)
    print(comp.bin)
    print(genome)
    genomeBlocks = [utils.readBlock(comp, i) for i in range(len(genome))]
    print(''.join(e["header"]["symbol"] for e in genomeBlocks))
    #pp.pprint(genomeBlocks)



