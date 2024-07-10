import sys

class header:
    magic = None
    endian = None
    hsize = None
    rev = None
    fsize = None
    sec_size = None
    num_entr = None
    def print(self):
        print("magic word = %s" % self.magic)
        print("file endian = %s" % self.endian)
        print("header size = %d" % self.hsize)
        print("revision = %d" % self.rev)
        if self.fsize != None:
            print("file size = %d" % self.fsize)
        if self.sec_size != None:
            print("section size = %d" % self.sec_size)
        print("entries = %d" % self.num_entr)

class section:
    offset = None
    header = None
    entries = []
    def __init__(self, h):
        self.header = h
    def get_type(self):
        if self.header != None:
            return self.header.magic
    def get_entries(self):
        return self.entries
        
# Main CGFX section
cgfx = section(header())

####################
def getbyte(arr, idx):
    integer = arr[idx]
    return integer.to_bytes(1)
    
def ba2int(arr, endian):
    intarr = []
    for i in range(len(arr)):
        intarr.append(arr[i])
    if endian == "little":
        intarr.reverse()
    elif endian == "big":
        pass
    else:
        pass # error
    return int(bytearray(intarr).hex(), 16)
    
########################################################################################################################
def get_cgfx_header(ba):
    global cgfx
    # building file's main header
    magic = ba[:4]
    endian = ba[4:6]
    hsize = ba[6:8]
    rev = ba[8:12]
    fsize = ba[12:16]
    num_entr = ba[16:20]

    cgfx.header.magic = magic.decode()
    if endian[0] > endian[1]:
        cgfx.header.endian = "little"
    else:
        cgfx.header.endian = "big"
    
    cgfx.header.hsize = ba2int(hsize, "little")
    cgfx.header.rev = ba2int(rev, "big")
    cgfx.header.fsize = ba2int(fsize, "little")
    cgfx.header.num_entr = ba2int(num_entr, "little")
    cgfx.offset = 0x00
    
    # getting main entries
    for e in range(cgfx.header.num_entr):
        pass #TODO
    
def main():
    global cgfx

    args = sys.argv[1:]
    if len(args) > 0:
        infile = open(args[0], "rb")
        fba = bytearray(infile.read()) # file byte array
        get_cgfx_header(fba)
        
        print(cgfx.get_type())
        print(cgfx.get_entries())
        
if __name__ == "__main__":
    exit(main())
