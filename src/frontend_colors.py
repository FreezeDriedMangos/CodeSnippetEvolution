
COLORS = {
    "background": "#202020",
    "foreground": "#aaaaaa",
    "life":         "#0d5922",
    "block update": "#636902"
    } 


def rgbToHex(r, g, b):
    r = int(r)
    g = int(g)
    b = int(b)
    
    r = hex(r)[2:]
    r = r if len(r) > 1 else "0"+r
    
    g = hex(g)[2:]
    g = g if len(g) > 1 else "0"+g
    
    b = hex(b)[2:]
    b = b if len(b) > 1 else "0"+b
    
    return "#"+r+g+b


hexi = {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, 
        "a": 10, "b": 11, "c":12, "d":13, "e":14, "f":15, 
        "A": 10, "B": 11, "C":12, "D":13, "E":14, "F":15}
def hexToRGB(hexCode):
    assert(type(hexCode) == str)
    if hexCode[0] == '#':
        hexCode = hexCode[1:]
    assert(len(hexCode) == 6)
        
    r = 16 * hexi[hexCode[0]] + hexi[hexCode[1]]
    g = 16 * hexi[hexCode[2]] + hexi[hexCode[3]]
    b = 16 * hexi[hexCode[4]] + hexi[hexCode[5]]
    
    return (r, g, b)
    
    
def colorLerp(hex1, hex2, percentage):
    assert(type(hex1) == str)
    assert(type(hex2) == str)
    assert(type(percentage) == float or type(percentage) == int)
    assert(0 <= percentage and percentage <= 1)
    
    p = percentage
    q = 1-percentage
    
    r1, g1, b1 = hexToRGB(hex1)
    r2, g2, b2 = hexToRGB(hex2)
    
    r3 = r2*p + r1*q
    g3 = g2*p + g1*q
    b3 = b2*p + b1*q
    
    hex3 = rgbToHex(r3, g3, b3)
    
    return hex3
    
    
