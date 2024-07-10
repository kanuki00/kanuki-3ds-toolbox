import sys

class prop:
    magic = "None"
    endian = "None"
    hsize = 0
    rev = 0
    fsize = 0
    num_entr = 0
    def print(self):
        print("magic word = %s" % self.magic)
        print("file endian = %s" % self.endian)
        print("header size = %d" % self.hsize)
        print("revision = %d" % self.rev)
        print("file size = %d" % self.fsize)
        print("entries = %d" % self.num_entr)

cgfx_prop = prop()
####################
def getbyte(arr, idx):
    integer = arr[idx]
    return integer.to_bytes(1)
    
def a(arr, endian):
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
###################
def cgfx_header(ba):
    global cgfx_prop

    magic = ba[:4]
    endian = ba[4:6]
    hsize = ba[6:8]
    rev = ba[8:12]
    fsize = ba[12:16]
    num_entr = ba[16:20]

    cgfx_prop.magic = magic.decode()
    if endian[0] > endian[1]:
        cgfx_prop.endian = "little"
    else:
        cgfx_prop.endian = "big"
    
    cgfx_prop.hsize = a(hsize, "little")
    cgfx_prop.rev = a(rev, "big")
    cgfx_prop.fsize = a(fsize, "little")
    cgfx_prop.num_entr = a(num_entr, "little")
    
def main():
    global cgfx_prop

    args = sys.argv[1:]
    if len(args) > 0:
        infile = open(args[0], "rb")
        fba = bytearray(infile.read())
        cgfx_header(fba)
        cgfx_prop.print()
        
if __name__ == "__main__":
    exit(main())
