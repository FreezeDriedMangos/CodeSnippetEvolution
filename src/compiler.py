
import re
import opcode
from opcode import *
import utils

def genomeSymbolsFromFile(filepath):
    genomeString = open(filepath, 'r').read()
    genomeString = re.sub(r"(\/\/.*\n)|(\/\/.*)| |\n", "", genomeString)
    return genomeString


def readSpawnTableFromFile(filepath):
    if filepath is None or filepath == "":
        return None
    
    try:
        spawnTableString = open(filepath, 'r').read()
        spawnTableString = re.sub(r"(\/\/.*\n)|(\/\/.*)", "", spawnTableString)
        
        print(spawnTableString)
        
        spawnTable = [e.split('\t') for e in spawnTableString.split('\n')]
        
        print(spawnTable)
        spawnTable = [(int(e[1]), e[0],) for e in spawnTable if len(e) == 2]
        return spawnTable
    except:
        print("ERROR reading in spawn table from file ", filepath)
        return None


def spawnTableFromGenome(genomeString):
    symbols = set(genomeString)
    counts = {s: 0 for s in symbols}
    
    for s in genomeString:
        counts[s] += 1
        
    return [(counts[s], s,) for s in counts]


# unit testing
if __name__ == "__main__":
    import pprint
    p = pprint.PrettyPrinter(indent=4)

    g = genomeSymbolsFromFile("genomes/anc1_1.gne")
    st = spawnTableFromGenome(g)
    #p.pprint(st)
    
    for e in st:
        print(e[1] + "\t" + str(e[0]))


