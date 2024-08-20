import sys
# ansi colors
color1 = "\033[38;5;214m"
color2 = "\033[38;5;123m"
# \033[0m reset

dicttypes = [
    "models", 
    "textures", 
    "luts", 
    "materials", 
    "shaders", 
    "cameras", 
    "lights", 
    "fog", 
    "environments", 
    "skeleton_animations", 
    "texture_animations", 
    "visibility_animations", 
    "camera_animations", 
    "light_animations", 
    "emitters", 
    "unknown"
]

class dictinfo:
    def __init__(self, t, ne, ro, e):
        self.type = t
        self.num_entries = ne
        self.relative_offset = ro
        self.end = e
    def print(self):
        print("%s%s, \033[0mentries: %d, relative offset: %s0x%s\033[0m, end: 0x%s" % (color2, self.type, self.num_entries, color2, self.relative_offset.to_bytes(4, "big").hex(), self.end.to_bytes(4, "big").hex()))

class cgfxdict:
    def __init__(self):
        self.magic = None
        self.size = None
        self.num_entries = None
        self.myst1 = None
        self.myst2 = None
        self.myst3 = None
        self.content = {}

class header:
    def __init__(self):
        self.magic = None
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
    dictinfos = []
    def print(self):
        header.print(self)
        if self.datasize != None:
            print("DATA size = %d bytes" % self.datasize)
        if len(self.dictinfos) > 0:
            for di in self.dictinfos:
                di.print()
            
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
        print("Section offset = %s0x%s" % (color1, self.offset.to_bytes(4, "big").hex()))


infile_name = ""        
# Main CGFX section
cgfx = section(cgfx_header())

####################
def getbyte(arr, idx):
    integer = arr[idx]
    return integer.to_bytes(1, "big")
    
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
    
def print_file_info():
    global infile_name
    print("File \"%s\"" % (infile_name))
    print("")
    cgfx.print_offset()
    cgfx.header.print()
    print("")
    for entry in cgfx.entries:
        entry.print_offset()
        entry.header.print()
        print("")
    
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
            b0 = ba[i].to_bytes(1, "big")
            b1 = ba[i+1].to_bytes(1, "big")
            b2 = ba[i+2].to_bytes(1, "big")
            b3 = ba[i+3].to_bytes(1, "big")
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
                    for j in range(16):
                        neoff = i+8+j*8 # dict num entries offset
                        roffoff = i+12+j*8 # dict relative offset offset
                        type = dicttypes[j]
                        neb = ba[neoff:neoff+4]
                        num_entries = ba2int(neb, cgfx.header.endian)
                        rob = ba[roffoff:roffoff+4]
                        relative_offset = ba2int(rob, cgfx.header.endian)
                        temphead.dictinfos.append(dictinfo(type, num_entries, relative_offset, roffoff+4))

                elif magic == "IMAG":
                    temphead = imag_header()
                    
                temphead.magic = magic
                
                tempsec = section(temphead)
                tempsec.offset = i
                tempsec.entries = []
                
                cgfx.entries.append(tempsec)
                prev_off = i
                break
    
    # populating main entries
    for e2 in cgfx.entries:
        if e2.header.magic == "DATA":
            for i in range(len(e2.header.dictinfos)):
                di = e2.header.dictinfos[i]
                tempcgfxdict = cgfxdict()
                
                
                
                e2.entries.append(tempcgfxdict)
            #print(e2.header.magic)
            #print(e2.get_entries())
            
        
def main():
    global cgfx
    global infile_name
    args = sys.argv[1:]
    if len(args) > 0:
        infile_name = args[0]
        infile = open(infile_name, "rb")
        fba = bytearray(infile.read()) # file byte array
        build_section_hierarchy(fba)
        print_file_info()
        
if __name__ == "__main__":
    exit(main())
