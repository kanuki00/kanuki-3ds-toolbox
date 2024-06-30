import sys

def get_valid_magic(filename):
    ifm=open(filename, "rb")
    magic = ifm.read(4).decode('utf-8') # read first 4 bytes and decode to string
    ifm.close
    if magic == 'PSLB': 
        return True
    else:
        return False
    

def convert(filename):
    if get_valid_magic(filename):
        infile = open(filename, "rb") # read bytes
        
        ba = bytearray(infile.read())
        
        for i in range(16, len(ba)):
            byte = ba[i].to_bytes(1)
            #if byte == b'\x02':
            #    print("int32")
            #if byte == b'\x03':
            #    print("float")
            #else:
            print(byte)
    else:
        print("Invalid magic word!")

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
        
    return 0
    
if __name__ == "__main__":
    exit(main())