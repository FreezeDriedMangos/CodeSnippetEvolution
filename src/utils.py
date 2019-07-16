
def binaryToInt(string, signedPlace=-1):
    placeValue = 1
    value = 0
    i = 0
    
    for bit in string[:-1]:
        if i == signedPlace:
            placeValue *= -1
            
        value += int(bit) * placeValue
        placeValue *= 2
        i += 1
        
    return value
        
    
def intToBinaryUnsigned(val, length):    
    placeValue = 2 ** length
    retval = ""
    
    for i in range(length):
        if val >= placeValue:
            val -= placeValue
            retval += "1"
        else:
            retval += "0"
            
        placeValue /= 2
    return retval
