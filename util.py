from binascii import unhexlify, hexlify
import hashlib
import struct

"""
struct format 

short : h (2byte)
unsigned short : H (2byte)
int : i (4bytes)
unsigned int : I (4bytes)
longlong : l (8bytes)
unsigned longlong : L (8bytes)

> big-endian
< little-endian

"""

class commonUtil():
    def __init__(self):
        pass

    def parsing_to_uint64_t(self, x):
        byte_array = unhexlify(x)
        if len(byte_array) != 8:
            raise ValueError("8바이트가 아닌 값이 들어왔습니다.")
    
        return struct.unpack("<Q", byte_array)[0]

    def parsing_to_int64_t(self, x):
        byte_array = unhexlify(x)
        if len(byte_array) != 8:
            raise ValueError("8바이트가 아닌 값이 들어왔습니다.")
        
        return struct.unpack("<q", byte_array)[0]

    def concatenate_byte(self, x, y):
        return x + y

    def double_hash(self, x):
        return hashlib.sha256(hashlib.sha256(x).digest()).hexdigest()

    def parsing_to_uint16_t(self, x):
        byte_array = unhexlify(x)
        if len(byte_array) != 4:
            raise ValueError("2바이트가 아닌 값이 들어왔습니다.")
        
        return struct.unpack("<H", byte_array)[0]

    def parsing_to_int16_t(self, x):
        byte_array = unhexlify(x)
        if len(byte_array) != 4:
            raise ValueError("2바이트가 아닌 값이 들어왔습니다.")
        
        return struct.unpack("<h", byte_array)[0]

    def parsing_to_uint32_t(self, x):
        byte_array = unhexlify(x)
        if len(byte_array) != 4:
            raise ValueError("4바이트가 아닌 값이 들어왔습니다.")
        
        return struct.unpack("<I", byte_array)[0]

    def parsing_to_int32_t(self, x):
        byte_array = unhexlify(x)
        if len(byte_array) != 4:
            raise ValueError("4바이트가 아닌 값이 들어왔습니다.")
        
        return struct.unpack("<i", byte_array)[0]

    def slicing(self, byte_array, start_index, size):
        return byte_array[start_index * 2 : (start_index + size) * 2]

    def slicing_and_get_offset(self, byte_array, start_index, size):
        return (byte_array[start_index * 2 : (start_index + size) * 2], start_index + size)

    def get_all_bytes(self, byte_array, start_index):
        return byte_array[start_index * 2 : ]

    def big_endian_to_little_endian(self, x):
        return ''.join(reversed([x[i:i+2] for i in range(0, len(x), 2)]))

    def big_endian_to_little_endian_number(self, x):
        return int(''.join(reversed([x[i:i+2] for i in range(0, len(x), 2)])), 16)

    def big_endian(self, x):
        return int(x, 16)

    def get_compact_size(self, x):
        check_value = self.big_endian_to_little_endian_number(x[:2])
        # print("이게 check value ", check_value)
        if check_value < 0xFD:
            return (self.big_endian_to_little_endian_number(x[:1 * 2]), 1)
        elif check_value == 0xFD:
            return (self.big_endian_to_little_endian_number(x[1*2:3 * 2]), 3)
        elif check_value == 0xFE:
            return (self.big_endian_to_little_endian_number(x[1*2:5 * 2]), 5)
        elif check_value == 0xFF:
            return (self.big_endian_to_little_endian_number(x[1*2:9 * 2]), 9)
    
common_util = commonUtil()


