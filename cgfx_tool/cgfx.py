import sys
color1 = "\033[93m"

class header:
    magic = None
    def print(self):
        if self.magic != None:
            print("Magic word = %s%s" % (color1, self.magic))
    
class cgfx_header(header):
    endian = None
    hsize = None
    rev = None
    fsize = None
    num_entr = None
    def print(self):
        header.print(self)
        if self.endian != None:
            print("File endian = %s" % self.endian)
        if self.hsize != None:
            print("Header size = %d" % self.hsize)
        if self.rev != None:
            print("Revision = %d" % self.rev)
        if self.fsize != None:
            print("File size = %d bytes" % self.fsize)
        if self.num_entr != None:
            print("Number of entries = %d" % self.num_entr)
        
class data_header(header):
    datasize = None
    models_dict_num_entries = None
    models_dict_reloff = None
    textures_dict_num_entries = None
    textures_dict_reloff = None
    luts_dict_num_entries = None
    luts_dict_reloff = None
    
    def print(self):
        header.print(self)
        if self.datasize != None:
            print("DATA size = %d bytes" % self.datasize)
        if self.models_dict_num_entries != None:
            print("Models dictionary entries count = %d" % self.models_dict_num_entries)
        if self.models_dict_reloff != None:
            print("Models dictionary relative offset = 0x%s" % self.models_dict_reloff.to_bytes(4).hex())
            
class imag_header(header):
    pass

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
    def print_offset(self):
        print("Section offset = %s0x%s" % (color1, self.offset.to_bytes(4).hex()))
        
# Main CGFX section
cgfx = section(cgfx_header())

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
def build_section_hierarchy(ba):
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
    cgfx.offset = 0
    
    # getting main entries
    prev_off = 0
    for e in range(cgfx.header.num_entr):
        for i in range(prev_off+4, len(ba)):
            b0 = ba[i].to_bytes(1)
            b1 = ba[i+1].to_bytes(1)
            b2 = ba[i+2].to_bytes(1)
            b3 = ba[i+3].to_bytes(1)
            try:
                b0 = b0.decode("utf-8")
                b1 = b1.decode("utf-8")
                b2 = b2.decode("utf-8")
                b3 = b3.decode("utf-8")
            except UnicodeDecodeError:
                continue
            magic = b0+b1+b2+b3
            if magic == "DATA" or magic == "IMAG":
                # i is the sections offset
                temphead = header()
                if magic == "DATA":
                    temphead = data_header()
                    dsb = ba[i+4:i+8] # datasize bytes. at offset 0x4, length is 0x4
                    temphead.datasize = ba2int(dsb, cgfx.header.endian)
                    mdne = ba[i+8:i+12]
                    mdro = ba[i+12:i+16]
                    temphead.models_dict_num_entries = ba2int(mdne, cgfx.header.endian)
                    temphead.models_dict_reloff = ba2int(mdro, cgfx.header.endian)
                elif magic == "IMAG":
                    temphead = imag_header()
                temphead.magic = magic
                
                tempsec = section(temphead)
                tempsec.offset = i
                
                cgfx.entries.append(tempsec)
                prev_off = i
                break

def main():
    global cgfx

    args = sys.argv[1:]
    if len(args) > 0:
        infile = open(args[0], "rb")
        fba = bytearray(infile.read()) # file byte array
        build_section_hierarchy(fba)
        
        cgfx.print_offset()
        cgfx.header.print()
        print("")
        for sec in cgfx.entries:
            sec.print_offset()
            sec.header.print()
            print("")
        
if __name__ == "__main__":
    exit(main())
