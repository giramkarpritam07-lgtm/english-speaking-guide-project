import sys
import struct

print(f"Python: {sys.version}")
print(f"Architecture: {struct.calcsize('P') * 8}-bit")
print(f"Installation: {sys.base_prefix}")
