from opcode import Opcodes

o = Opcodes()
symb = []
codes = []
types = {}

for f in o.FLAG_CODES: 
    e = o.FLAG_CODES[f]
    codes.append(e["code"])  
    symb.append(e["symbol"]) 
    
    if e["type"] in types:
        types[e["type"]].append(e["symbol"])
    else:
        types.update({e["type"]: [e["symbol"]]})
    

for f in o.INSTRUCTIONS:                    
    symb.append(f["symbol"])                
    codes.append(f["code"])   
    
    if f["type"] in types:
        types[f["type"]].append(f["symbol"])
    else:
        types.update({f["type"]: [f["symbol"]]})
        

import pprint  
pp = pprint.PrettyPrinter(indent=4)

pp.pprint(types)
   

for cat in types:
    print('    <list name="'+cat+'">')
    
    for item in types[cat]:
        if item is not None:
            print('      <item> '+item+' </item>')
    
    print('    </list>')
    
    
    
