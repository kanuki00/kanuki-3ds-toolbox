import sys

##################
printbytes = []
my_chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_@'
for c in my_chars:
    printbytes.append(c.encode('utf-8'))
##################
'''
The string type is a combination of an uint32 for the length of 
the string followed by the characters of the string.

For the Map and List after the type a uint32 follows that 
represents the number of entries in the Map/List.

The keys of the Map are always strings but the values can have 
any type of the table 

0x01 = String
0x02 = int32
0x03 = float (4 byte)
0x04 = Byte
0x05 = Map
0x06 = List
'''
##################

comp = 0            # comp = compose
string_flag = False
int32_flag = False
float_flag = False
byte_flag = False
map_flag = False
list_flag = False

int32_literal = 0
possible_string_flag = False
map_key_flag = False
     
def iflb(bytes, little_endian): # iflb = int from loose bytes
    intarr = []
    for byte in bytes:
        intarr.append(int.from_bytes(byte))
    if little_endian:
        intarr.reverse()
    arr = bytearray(intarr)
    return int(arr.hex(), 16)

def convert(filename):
    file = open(filename, "rb")
    fba = bytearray(file.read())    # file byte array
    fba_len = len(fba)              # file byte array length
    
    global comp
    global string_flag
    global int32_flag
    global byte_flag
    global list_flag
    global map_key_flag
    global possible_string_flag
    
    for i in range(16, fba_len):    # ignoring header by starting i at 16
        byte = fba[i].to_bytes(1)
        
        if comp > 0:
            comp -= 1
            
        # Checking byte
        if byte == b'\x01' and comp == 0:
            possible_string_flag = True
        if byte != b'\x00' and comp == 0 and byte not in printbytes:
            stage1 = True
            if i+1 >= fba_len:
                stage1 = False
            if i+4 >= fba_len:
                stage1 = False
            if stage1:
                nxbyte = fba[i+1].to_bytes(1)
                pstrlen = iflb([byte, nxbyte], True)        # possible string length
                ssbyte = fba[i+4].to_bytes(1)               # string start byte
#                 try:
#                     print("pstrlen = %s, startbyte = %s" % (str(pstrlen), ssbyte.decode('utf-8')))
#                 except UnicodeDecodeError:
#                     print("pstrlen = %s, Unicode decode error" % (str(pstrlen)))
                
                stage2 = True  
                if i+3+pstrlen >= fba_len:
                    stage2 = False
                if ssbyte not in printbytes:
                    stage2 = False
                if stage2:
                    stage3 = True
                    for j in range(pstrlen):
                        testbyte = fba[i+4+j].to_bytes(1)
                        if testbyte not in printbytes:
                            stage3 = False
#                        print(testbyte.decode('utf-8'))
                    if stage3 and possible_string_flag:
                        string_flag = True
                        possible_string_flag = False
                    elif stage3:
                        map_key_flag = True
        if byte == b'\x02' and comp == 0 and not map_key_flag:
            int32_flag = True
            stage1 = True
            if i+4 >= fba_len:
                stage1 = False
            if stage1:
                db1 = fba[i+1].to_bytes(1)
                db2 = fba[i+2].to_bytes(1)
                db3 = fba[i+3].to_bytes(1)
                db4 = fba[i+4].to_bytes(1)
                int32_literal = iflb([db1, db2, db3, db4], True)
            comp = 4
        if byte == b'\x04' and comp == 0 and not map_key_flag:
            byte_flag = True
            comp = 2
        if byte == b'\x05' and comp == 0 and not map_key_flag:
            map_flag = True
            comp = 4
        if byte == b'\x06' and comp == 0 and not map_key_flag:
            list_flag = True 
            comp = 4
            
        # Printing
        if byte in printbytes and not int32_flag:
            print(byte.decode('utf-8'))
        else:
            type = ""
            # INT32
            if int32_flag and comp == 4:
                type = "int32 (value=%d)" % (int32_literal)
                int32_literal = 0
            if int32_flag and comp == 0:
                type = "int32 end"
                int32_flag = False
            # BYTE
            if byte_flag and comp == 2:
                type = "Byte"
            if byte_flag and comp == 1:
                type = "Byte end"
                byte_flag = False
            # MAP
            if map_flag and comp == 4:
                type = "Map"
            if map_flag and comp == 0:
                type = "Map end"
                map_flag = False
            # LIST            
            if list_flag and comp == 4:
                type = "List"
            if list_flag and comp == 0:
                type = "List end"
                list_flag = False

                
            if string_flag:
                type = "String"
                string_flag = False            
            if map_key_flag:
                type = "Map key"
                map_key_flag = False
                
            print("0x%s %s" % (byte.hex(), type))
            
        
def main():
    args = sys.argv[1:]
    convert(args[0])
    return 0
    
if __name__ == "__main__":
    exit(main())