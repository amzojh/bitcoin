from util import common_util, unhexlify, hexlify
from block_header import blockHeader
from transaction import transaction

"""
[ magic bytes ][    size     ][        block header        ][  tx count  ][          transaction data          ]
 <- 4 bytes ->  <- 4 bytes ->  <-        80 bytes        ->  <- varint ->  <-            remainder           ->
magic bytes 는 항상 f9beb4d9이 값을 가져야 함. 아니면 오류

b'\xf9\xbe\xb4\xd9' 반드시 이 값이어야함 !!!
size 
"""
"""
Value	Bytes Used	Format
>= 0 && <= 252	1	uint8_t
>= 253 && <= 0xffff	3	0xfd followed by the number as uint16_t
>= 0x10000 && <= 0xffffffff	5	0xfe followed by the number as uint32_t
>= 0x100000000 && <= 0xffffffffffffffff	9	0xff followed by the number as uint64_t
"""

"""
class 정의 
offset : byte를 읽어들이는 

magic_byte : 구분자
size : 블록의 사이즈
block_header : 블록헤더 (구현부 block_header.py)
tranaction_list : transaction들
block_hash : 현재 block의 hash값 (block header에 있는 merkle root를 이용하여 얻은 값)
calculated_merkle_root : transaction_id를 통해서 얻은 merkle_root
calculated_block_hash : 직접계산한 merkle_root와 header 정보로 만든 현재 block의 hash 값
"""



class bitcoinObject:
    
    def __init__(self, byte_array):
        self.common_util = common_util
        self.original_byte = byte_array
        # print(self.original_byte)

        offset = 0

        self.magic_byte, offset = self.common_util.slicing_and_get_offset(byte_array, offset, 4)
        self.size, offset = self.common_util.slicing_and_get_offset(byte_array, offset, 4) # 4바이트 ~ 8바이트
        self.block_header = blockHeader(self.common_util.slicing(byte_array, offset, 80))
        
        # print(self.block_header.get_dict())

        offset = offset + 80
        self.transaction_count, transaction_offset = self._parsing_transaction_count(self.common_util.slicing(byte_array, offset, 9))
        offset = offset + transaction_offset
        self.transaction_list = self._parsing_transaction(self.common_util.get_all_bytes(byte_array=byte_array, start_index=offset), self.transaction_count)
        self.calculated_merkle_root = self._process_merkle_root()
        self.block_hash = self.block_header.calculate_hash_without_merkle_root()
        self.calculated_block_hash = self.block_header.calculate_hash_with_merkle_root(self.calculated_merkle_root)
        offset = offset + self._get_list_element_size(self.transaction_list)
        self.offset = offset

    def get_size(self):
        return self.offset

    def _get_tx_list(self):
        tx_list = []
        for tx in self.transaction_list:
            if tx.isCoinbase:
                coinbase = []
                coinbase.append(tx.transaction_id)
                tx_list = coinbase + tx_list
            else:
                tx_list.append(tx.transaction_id)
        return tx_list

    def _process_merkle_root(self):
        tx_list = self._get_tx_list()
        isCompleted = False
        cnt = 0
        while not isCompleted:
            # coinbase 만이 있는 경우에는 바로 return
            if cnt == 0 and len(tx_list) == 1:
                return tx_list.pop(0)

            tx_list = self._calculate_merkle_root(tx_list)
            if len(tx_list) == 1:
                isCompleted = True

            cnt += 1

        if len(tx_list) != 1:
            raise ValueError("Error")

        return tx_list.pop(0)            

    def _calculate_merkle_root(self, tx_list):
        if len(tx_list) % 2 == 1:
            tx_list.append(tx_list[-1])

        loop_cnt = int(len(tx_list) / 2)
        merkle_list = []

        for i in range(loop_cnt):
            first_intx = tx_list.pop(0)
            second_intx = tx_list.pop(0)
            concatenated_intx = self.common_util.concatenate_byte(first_intx, second_intx)
            concatenated_intx = unhexlify(concatenated_intx)
            hashed_intx = self.common_util.double_hash(concatenated_intx)
            merkle_list.append(hashed_intx)

        return merkle_list
        

    def _get_list_element_size(self, tx_list):
        size = 0
        for tx in tx_list:
            size = size + tx.get_size()

        return size

    def _parsing_transaction_count(self, byte_array):
        return self.common_util.get_compact_size(byte_array)

    def _parsing_transaction(self, byte_array, count):
        transaction_list = []
        data_length = int(len(byte_array) / 2)
        data_from = 0
        data_to = data_length
        for i in range(count):
            transaction_obj = transaction(self.common_util.slicing(byte_array, data_from, data_to))
            data_from += transaction_obj.get_size()
            transaction_list.append(transaction_obj)

        return transaction_list

    def _get_list_string(self, obj_list):
        expression =""
        for obj in obj_list:
            expression += str(obj)

        return expression


    def _get_list_dict(self, obj_list):
        dict_list = []
        for obj in obj_list:
            dict_list.append(obj.get_dict())
        
        return dict_list

    def __str__(self):
        return f"""
    magic_byte : {str(self.common_util.big_endian_to_little_endian(self.magic_byte))}
    block_size : {str(self.common_util.big_endian_to_little_endian_number(self.size))}
    blockHeader: {str(self.block_header)}
    transaction_cnt : {str(self.transaction_count)}
    transaction : {self._get_list_string(self.transaction_list)}
            """     

    def get_dict(self):
        return {
            "magic_byte" : self.common_util.big_endian_to_little_endian(self.magic_byte),
            "block_size" : self.common_util.big_endian_to_little_endian_number(self.size),
            "blockHeader" : self.block_header.get_dict(),
            "transaction_cnt" : self.transaction_count,
            "transaction" : self._get_list_dict(self.transaction_list),
            "calculated_merkle_root" : self.common_util.big_endian_to_little_endian(self.calculated_merkle_root),
            "calculated_block_hash" : self.common_util.big_endian_to_little_endian(self.calculated_block_hash),
            "block_hash" : self.common_util.big_endian_to_little_endian(self.block_hash),
        }