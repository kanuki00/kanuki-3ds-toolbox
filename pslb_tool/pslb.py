import sys
import struct

##################################
### Global variables and flags ###
##################################
printbytes = []
my_chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_@'
for c in my_chars:
    printbytes.append(c.encode('utf-8'))

comp = 0            # comp = compose
string_flag = False
int32_flag = False
float_flag = False
byte_flag = False
map_flag = False
list_flag = False

string_len = 0
string_literal = ""
int32_literal = 0
float_literal = 0.0
byte_literal = 0
map_keycount = 0
list_entriescount = 0
map_key_flag = False
map_key_string_len = 0
map_key_string_literal = ""

class fo:
    def __init__(self, type, size):
        self.type = type
        self.size = size
formatstack = []
mapkey_format_flag = False
mapkey_type_store = ""
mapkey_tabs_store = ""

########################
### Helper functions ###
########################
def iflb(bytes, little_endian): # iflb = int from loose bytes
    intarr = []
    for byte in bytes:
        intarr.append(int.from_bytes(byte))
    if little_endian:
        intarr.reverse()
    arr = bytearray(intarr)
    return int(arr.hex(), 16)
    
def int32get(bytearray, index):
    db1 = bytearray[index+1].to_bytes(1) # data byte 1
    db2 = bytearray[index+2].to_bytes(1) # data byte 2
    db3 = bytearray[index+3].to_bytes(1) # data byte 3
    db4 = bytearray[index+4].to_bytes(1) # data byte 4
    return iflb([db1, db2, db3, db4], True) # return int that these bytes represent. in little endian form.
    
def tabstring(count):
    result = ""
    for i in range(count):
        result+="\t"
    return result
    
def formattype(base, instgtype, instgsize):
    
    global mapkey_format_flag
    global mapkey_tabs_store
    global formatstack
    if mapkey_format_flag:
        mapkey_tabs_store = tabstring(len(formatstack))
    tabbedbase = "%s%s" % (tabstring(len(formatstack)), base)    
    result = ""
    
    if instgtype == "map":
        if len(formatstack) > 0:
            formatstack[0].size -= 1
        formatstack.insert(0, fo("map", instgsize))
        if mapkey_format_flag:
            result = "%s\n%s{" % (base, tabstring(len(formatstack)-1))
        else:
            result = "%s\n%s{" % (tabbedbase, tabstring(len(formatstack)-1))
    elif instgtype == "list":
        if len(formatstack) > 0:
            formatstack[0].size -= 1
        formatstack.insert(0, fo("list", instgsize))
        if mapkey_format_flag:
            result = "%s\n%s[" % (base, tabstring(len(formatstack)-1))
        else:
            result = "%s\n%s[" % (tabbedbase, tabstring(len(formatstack)-1))
    elif instgtype == "mapkey":
        mapkey_format_flag = True
    elif instgtype == "string" or instgtype == "int32" or instgtype == "float" or instgtype == "byte":
#         match formatstack[0].type:
#             case "list":
#                 formatstack[0].size -= 1
#             case "map":
#                 formatstack[0].size -= 1
        if len(formatstack) > 0:
            formatstack[0].size -= 1
        if mapkey_format_flag:
            result = "%s" % (base)
        else:
            result = "%s" % (tabbedbase)
    else:
        pass
    return result

########################
### Convert function ###
########################
def convert(filename, outfilename):
    file = open(filename, "rb")
    fba = bytearray(file.read())    # file byte array
    fba_len = len(fba)              # file byte array length
    outputfile = open(outfilename, "w")
    
    global comp
    global string_flag
    global int32_flag
    global float_flag
    global byte_flag
    global list_flag
    global map_key_flag
    global mapkey_format_flag
    global mapkey_type_store
    global mapkey_tabs_store
    
    i = 16
    #for i in range(16, fba_len):    # ignoring header by starting i at 16
    while i < fba_len:
        if len(formatstack) > 0:
            if formatstack[0].size <= 0:
                if formatstack[0].type == "map":
                    outputfile.write("%s}\n" % (tabstring(len(formatstack)-1)))
                else:
                    outputfile.write("%s]\n" % (tabstring(len(formatstack)-1)))
                del formatstack[0]
                continue

        byte = fba[i].to_bytes(1)
        
        if comp > 0:
            comp -= 1
            
        #####################  
        ### Checking byte ###
        #####################
        # MapKey
        if byte not in printbytes and comp == 0:
            stage1 = True                                   ### STAGE 1
            if i+1 >= fba_len:
                stage1 = False
            if i+4 >= fba_len:
                stage1 = False
            if stage1:
                stage2 = True                               ### STAGE 2
                db2 = fba[i+1].to_bytes(1)
                db3 = fba[i+2].to_bytes(1)
                db4 = fba[i+3].to_bytes(1)
                pstrlen = iflb([byte, db2, db3, db4], True) # possible string length
                ssbyte = fba[i+4].to_bytes(1)               # string start byte
                if i+3+pstrlen >= fba_len:
                    stage2 = False
                if ssbyte not in printbytes:
                    stage2 = False
                if stage2:
                    stage3 = True                           ### STAGE 3
                    pstr = ""                               # possible string
                    for j in range(pstrlen):
                        testbyte = fba[i+4+j].to_bytes(1)
                        if testbyte not in printbytes:
                            stage3 = False
                        else:
                            pstr+=testbyte.decode('utf-8')
                    if stage3:
                        map_key_flag = True                 ### GOAL
                        map_key_string_len = pstrlen
                        map_key_string_literal = pstr
                        comp = 3 + map_key_string_len
        # String
        if byte == b'\x01' and comp == 0:
            string_flag = True
            string_len = int32get(fba, i)
            string_literal = ""
            for j in range(string_len):
                decodebyte = fba[i+5+j].to_bytes(1)
                try:
                    string_literal+=decodebyte.decode('utf-8')
                except UnicodeError:
                    string_literal+='?'
            comp = 4 + string_len
        # Int32
        if byte == b'\x02' and comp == 0 and not map_key_flag:
            int32_flag = True
            stage1 = True
            if i+4 >= fba_len:
                stage1 = False
            if stage1:
                int32_literal = int32get(fba, i)
            comp = 4
        # Float
        if byte == b'\x03' and comp == 0 and not map_key_flag:
            float_flag = True
            stage1 = True
            if i+4 >= fba_len:
                stage1 = False
            if stage1:
                intarr = []
                intarr.append(int.from_bytes(fba[i+1].to_bytes(1)))
                intarr.append(int.from_bytes(fba[i+2].to_bytes(1)))
                intarr.append(int.from_bytes(fba[i+3].to_bytes(1)))
                intarr.append(int.from_bytes(fba[i+4].to_bytes(1)))
                intarr.reverse() # reverse because we want little endian
                floathex = bytearray(intarr).hex()
                float_literal = struct.unpack('!f', bytes.fromhex(floathex))[0]
            comp = 4
        # Byte
        if byte == b'\x04' and comp == 0 and not map_key_flag:
            byte_flag = True
            nextbyte = fba[i+1].to_bytes(1)
            byte_literal = int.from_bytes(nextbyte)
            comp = 2
        # Map
        if byte == b'\x05' and comp == 0 and not map_key_flag:
            map_flag = True
            map_keycount = int32get(fba, i)
            comp = 4
        # List
        if byte == b'\x06' and comp == 0 and not map_key_flag:
            list_flag = True
            list_entriescount = int32get(fba, i)
            comp = 4
        ################
        ### Printing ###
        ################
        type = ""
        should_print = False
        
        # STRING
        if string_flag and comp == 4 + string_len:
            str_type_base = "String (length=%d, value=%s)" % (string_len, string_literal)
            type = formattype(str_type_base, "string", 0)
            should_print = True
        if string_flag and comp == 0:
            string_len = 0
            string_literal = ""
            string_flag = False
            should_print = False
        # INT32
        if int32_flag and comp == 4:
            int32_type_base = "int32 (value=%d)" % (int32_literal)
            type = formattype(int32_type_base, "int32", 0)
            should_print = True
        if int32_flag and comp == 0:
            type = "int32 end"
            int32_literal = 0
            int32_flag = False
            should_print = False
        # FLOAT
        if float_flag and comp == 4:
            float_type_base = "float (value=%f)" % (float_literal)
            type = formattype(float_type_base, "float", 0)
            should_print = True
        if float_flag and comp == 0:
            float_literal = 0.0
            float_flag = False
            should_print = False
        # BYTE
        if byte_flag and comp == 2:
            byte_type_base = "Byte (value=%d)" % (byte_literal)
            type = formattype(byte_type_base, "byte", 0)
            should_print = True
        if byte_flag and comp == 1:
            type = "Byte end"
            byte_literal = 0
            byte_flag = False
            should_print = False
        # MAP
        if map_flag and comp == 4:
            map_type_base = "Map (keys=%d)" % (map_keycount)
            type = formattype(map_type_base, "map", map_keycount)
            should_print = True
        if map_flag and comp == 0:
            type = "Map end"
            map_keycount = 0
            map_flag = False
            should_print = False
        # LIST            
        if list_flag and comp == 4:
            list_type_base = "List (entries=%d)" % (list_entriescount)
            type = formattype(list_type_base, "list", list_entriescount)
            should_print = True
        if list_flag and comp == 0:
            type = "List end"
            list_entriescount = 0
            list_flag = False
            should_print = False
        # MAPKEY
        if map_key_flag and comp == 3 + map_key_string_len:
            type = "MapKey (string_length=%d, string_value=%s)" % (map_key_string_len, map_key_string_literal)
            formattype("", "mapkey", 0)
            should_print = True
        if map_key_flag and comp == 0:
            type = "MapKey end"
            map_key_string_len = 0
            map_key_string_literal = ""
            map_key_flag = False
            should_print = False
       
        if should_print:
            if mapkey_format_flag and mapkey_type_store == "":
                mapkey_type_store = type
            elif mapkey_format_flag and mapkey_type_store != "":
                outputfile.write("%s%s: %s\n" % (mapkey_tabs_store, mapkey_type_store, type))
                mapkey_format_flag = False
                mapkey_type_store = ""
                mapkey_tabs_store = ""
            else:
                outputfile.write("%s\n" % (type))
            
        i += 1
    if i == fba_len and len(formatstack) > 0:
        for f in formatstack:
            if f.type == "map":
                outputfile.write("}\n")
            else:
                outputfile.write("]\n")

def main():
    args = sys.argv[1:]
    convert(args[0], args[1])
    return 0
    
if __name__ == "__main__":
    exit(main())