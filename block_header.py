from util import common_util, unhexlify


"""
4	version	int32_t	The block version number indicates which set of block validation rules to follow. See the list of block versions below.
32	previous block header hash	char[32]	A SHA256(SHA256()) hash in internal byte order of the previous block’s header. This ensures no previous block can be changed without also changing this block’s header.
32	merkle root hash	char[32]	A SHA256(SHA256()) hash in internal byte order. The merkle root is derived from the hashes of all transactions included in this block, ensuring that none of those transactions can be modified without modifying the header. See the merkle trees section below.
4	time	uint32_t	The block time is a Unix epoch time when the miner started hashing the header (according to the miner). Must be strictly greater than the median time of the previous 11 blocks. Full nodes will not accept blocks with headers more than two hours in the future according to their clock.
4	nBits	uint32_t	An encoded version of the target threshold this block’s header hash must be less than or equal to. See the nBits format described below.
4	nonce	uint32_t	An arbitrary number miners change to modify the header hash in order to produce a hash less than or equal to the target threshold. If all 32-bit values are tested, the time can be updated or the coinbase transaction can be changed and the merkle root updated.
"""

class blockHeader:

    def __init__(self, byte_array):
        self.common_util = common_util
        self.original_byte = byte_array
        self.version = self.common_util.slicing(byte_array, 0, 4) # 4 byte
        self.previous_hash_block = self.common_util.slicing(byte_array, 4, 32) # 32 byte
        self.merkle_root = self.common_util.slicing(byte_array, 36, 32) # 32 byte merkel_root
        self.time_stamp = self.common_util.slicing(byte_array, 68, 4) # 4byte timestamp 
        self.bits = self.common_util.slicing(byte_array, 72, 4) # 4byte 어려움 정도
        self.nonce = self.common_util.slicing(byte_array, 76, 4)  # 4byte

    def calculate_hash_without_merkle_root(self):
        header = self.version + self.previous_hash_block + self.merkle_root + self.time_stamp + self.bits + self.nonce
        header = unhexlify(header)
        return self.common_util.double_hash(header)
    
    def calculate_hash_with_merkle_root(self, merkle_root):
        header = self.version + self.previous_hash_block + merkle_root + self.time_stamp + self.bits + self.nonce
        header = unhexlify(header)
        return self.common_util.double_hash(header)

    def __repr__(self):
        return f"""
            version : {self.common_util.big_endian_to_little_endian(self.version)}
            previous_hash_block : {self.common_util.big_endian_to_little_endian(self.previous_hash_block)}
            merkel_root : {self.common_util.big_endian_to_little_endian(self.merkle_root)}
            bits : {self.common_util.big_endian_to_little_endian(self.bits)}
            nonce : {self.common_util.big_endian_to_little_endian(self.nonce)}
        """
    def get_dict(self):
        return {
            "version" : self.common_util.parsing_to_uint32_t(self.version),
            "previous_hash_block" : self.common_util.big_endian_to_little_endian(self.previous_hash_block),
            "merkel_root" : self.common_util.big_endian_to_little_endian(self.merkle_root),
            "timestamp" : self.common_util.parsing_to_uint32_t(self.time_stamp),
            "bits" : self.common_util.parsing_to_uint32_t(self.bits),
            "nonce" : self.common_util.parsing_to_uint32_t(self.nonce),
            "correct_hash" : self.common_util.big_endian_to_little_endian(self.calculate_hash_without_merkle_root()),
        }