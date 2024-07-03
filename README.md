Nintendo LZ compression
=======================

This is a collection of tools for compressing and decompressing Nintendo's [LZSS][] formats, found in games such as Pokémon. MIT licensed.

[LZSS]: http://en.wikipedia.org/wiki/Lempel%E2%80%93Ziv%E2%80%93Storer%E2%80%93Szymanski

Supports: (Python 3)

* LZ10 (compression and decompression)
* LZ11 (compression and decompression)
* overlays (decompression only)

Python 2 support is less complete:

* LZ10 (decompression only)
* overlays (decompression only)


Note: Names are pretty inconsistent. I variously refer the compression algorithm as LZSS, LZSS10, LZ10 and NLZ10.

Files
-----

* `lzss3.py` - LZ decompression routines for Python 3. Can used as a module or a standalone script.
* `compress.py` - LZ compression routines for Python 3. Should be merged into lzss3.py. Command-line interface is spotty.
* `verify.py` - Script i threw together while trying to debug LZ11 compression. Should be merged into `lzss3.py`. Python 3.
* `lzss.py` - Incomplete LZ decompression routines for Python 2. Only supports LZ10.
* `armdecomp.py` - Command-line tool for decompressing overlays or arm9.bin. Python 2 version.
* `armdecomp3.py` - Command-line tool for decompressing overlays or arm9.bin. Python 3 version. About twice as fast as the Python 2 version. The code has already been merged into `lzss3.py`, so this file isn't really needed.
* `test_lzss3.py` - Tests for `lzss3.py` and `compress.py`.

DARCTool
========
This is a tool for extracting and building 3DS darc archive files. In some cases the file extension is ".arc". Remember, if the archive is compressed you must use another tool to handle that.  

Also note that when building archives, it goes by the order returned by readdir(), hence the order in the archive in some cases may not match the original official archive which was extracted previously. Due to this and alignment, the built archive filesize may not match the original official archive filesize either, but this doesn't actually matter.  

The utils.* and types.h files are from ctrtool.

PSLB Tool
=========
This is a tool for converting PSLB files into human readable json files. PSLB files often show up in games like "Kid Icarus: Uprising" with the extention .json, even though they are not actual json files.
Command line usage:
`python pslb.py [inputfile] [outputfile]`

Documentation of the PSLB format: [https://www.3dbrew.org/wiki/PSLB][]
[https://www.3dbrew.org/wiki/PSLB]: https://www.3dbrew.org/wiki/PSLB
