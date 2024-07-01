import sys

def get_valid_magic(filename):
    ifm=open(filename, "rb")
    magic = ifm.read(4).decode('utf-8') # read first 4 bytes and decode to string
    ifm.close()
    if magic == 'PSLB': 
        return True
    else:
        return False
        
def int_from_loose_bytes(bytes, little_endian):
    intarr = []
    for byte in bytes:
        intarr.append(int.from_bytes(byte))

    if little_endian:
        intarr.reverse()

    arr = bytearray(intarr)
    return int(arr.hex(), 16)

def convert(filename):
    if get_valid_magic(filename):
        infile = open(filename, "rb") # read bytes
        ba = bytearray(infile.read())
        
        #print(int_from_loose_bytes([b'\x5f', b'\x03'], False))
        skip = 0
        value_flag = False
        map_flag = False
        map_int_byte_count = 0
        map_int_bytes = []
        list_flag = False
        list_int_byte_count = 0
        list_int_bytes = []
        for i in range(16, len(ba)): # start at offset 0x10 to cut out header
            byte = ba[i].to_bytes(1)
            ###
            if byte == bytes.fromhex('00') and map_flag == False and list_flag == False:
                #value_flag = True
                print("some kind of value?")
                continue
            
            if byte == bytes.fromhex('05') and list_flag == False and value_flag == False:
                map_flag = True
                continue
            if map_flag and map_int_byte_count < 2:
                map_int_bytes.append(byte)
                map_int_byte_count += 1    
                if map_int_byte_count == 2:
                    print('Map, %3d entries' % (int_from_loose_bytes(map_int_bytes, True)))
                    map_flag = False
                    map_int_byte_count = 0
                    map_int_bytes = []
                    continue
                continue
                
            if byte == bytes.fromhex('06') and map_flag == False and value_flag == False:
                list_flag = True
                continue
            if list_flag and list_int_byte_count < 2:
                list_int_bytes.append(byte)
                list_int_byte_count += 1    
                if list_int_byte_count == 2:
                    print('List, %3d entries' % (int_from_loose_bytes(list_int_bytes, True)))
                    list_flag = False
                    list_int_byte_count = 0
                    list_int_bytes = []
                    continue
                continue
            
            #print(byte.hex())
            print(byte)
            
        infile.close()
    else:
        print("Invalid magic word!")
        
def bytedump(filename): # debug
    infile = open(filename, "rb") # read bytes
    ba = bytearray(infile.read())
    for b in ba:
        byte = b.to_bytes(1)
        print(byte)
    infile.close()

def main():
    args = sys.argv[1:]
    
    infile_name = ""
    infile_specified = False
    outfile_name = ""
    
    if len(args) == 0:
        print("No arguments! Use -h for help.")
    if "-h" in args or "--help" in args:
        print("Usage:\n-h or --help to display help\n-if specify input file\n-of specify output file")
    
    if "-if" in args:
        infile_index = args.index("-if")
        if len(args) > infile_index+1:
            infile_name = args[infile_index+1]
            infile_specified = True
        else:
            print("No input file specified after '-if' flag!")
            
    if "-of" in args:
            outfile_index = args.index("-of")
            if len(args) > outfile_index+1:
                outfile_name = args[outfile_index+1]
            else:
                print("No output file specified after '-of' flag!")
                
    if infile_specified:
        convert(infile_name)
        #bytedump(infile_name)
        
    return 0
    
if __name__ == "__main__":
    exit(main())