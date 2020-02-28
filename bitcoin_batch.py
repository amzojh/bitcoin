import os
import glob
import binascii

import datetime

from pprint import pprint
import pandas as pd

from util import common_util
from bitcoin_object import bitcoinObject

result_column = ["Filename", "BlockHash", "PreviousBlockHash","TransactionCnt", "Description"]

class bitcoinBatch():
    def __init__(self, dat_file_path, log_class):
        # string 정보
        # block size를 얻은 후, 그 블록사이즈만큼 parsing하여 bitcoin_object를 생성함
        # bitcoin_object는 해당 블록사이즈만큼을 가지며 이것을 파싱하여 version,size,blockheader,tx, 등 
        """
        file_path : csv file path
        result_df : 


        """
        self.file_path = dat_file_path
        self.result_df = pd.DataFrame(columns=result_column)
        self.hex_bytes = self._binary_file_to_hexadecimal_string_parsing(dat_file_path)
        self.common_util = common_util
        self.logger_class = log_class
        self.logger = log_class.get_logger()
        self._parsing_block_process()
        
    def _parsing_block_process(self):
        length_of_block_file_binary = len(self.hex_bytes) / 2
        size_from = 0
        size_to = 0
        cnt = 0
        self.logger.info(f"파일명 : {self.file_path} 읽기를 시작합니다.")
        # try:  
        while length_of_block_file_binary > size_to:
            block_size = self.common_util.big_endian_to_little_endian_number((self.common_util.slicing(self.hex_bytes, size_from + 4, 4)))
            size_to = size_to + block_size + 8 # magic byte + block size
            byte_block = self.common_util.slicing(self.hex_bytes, size_from, size_to - size_from)
            
            # print(self.hex_bytes)
            
            cnt = cnt + 1

            # print(str(size_from) + "  to  " + str(size_to))
            # print(byte_block)
            block = bitcoinObject(byte_block)
            block.get_dict()
                        

            # block_list.append(block)

            #["Filename", "BlockHash", "PreviousBlockHash","TransactionCnt", "Description"]
            result_data = [self.file_path.split("\\")[-1], block.block_hash, block.block_header.previous_hash_block, block.transaction_count,""]
            # print(result_data)
            self.result_df = self.result_df.append(pd.DataFrame(columns=result_column, data=[result_data]))
            # pprint(block.get_dict())

            """
            4가지 validation check 
            (1) size check v
            (2) merkle root 검증(직접계산 vs block정보) 
            (3) hash value 검증(직접계산 vs block정보)
            (4) magic byte 검증
            """
            self.validation_check(size_to - size_from, block)
            size_from = size_to
        # except:
        #     message = self.logger_class.set_error_message("예상치 못한 오류입니다.", self.file_path, f"{cnt}번째 블록에서 오류발생 (from : {size_from} size : {block_size + 8}\nraw_block_byte : {byte_block}")
        #     self.logger.critical(message)
        
        self.logger.info(f"파일명 : {self.file_path} 읽기를 종료합니다.")

    def validation_check(self, size, block):
        if not self.magicbyte_check(block):
            message = self.logger_class.set_error_message("매직바이트에러",self.file_path, block.get_dict())
            self.logger.critical(message)
            raise AssertionError("매직바이트가 틀립니다. block을 잘못 파싱했습니다.")
        
        if not self.size_check(size, block):
            message = self.logger_class.set_error_message("사이즈오류",self.file_path, block.get_dict())
            self.logger.critical(message)
            raise AssertionError("블록크기가 다릅니다. transaction/blockheader 부분이 잘못 파싱된 것 같습니다.")

        if not self.merkleroot_check(block):
            message = self.logger_class.set_error_message("머클루트계산오류",self.file_path, block.get_dict())
            self.logger.critical(message)
            raise AssertionError("Txid로 계산한 merkle root와 block헤더정보의 merkle root 값이 다릅니다. transaction을 확인하세요")
        
        if not self.hash_value_check(block):
            message = self.logger_class.set_error_message("해시값오류",self.file_path, block.get_dict())
            self.logger.critical(message)
            raise AssertionError("Txid로 계산한 merkle root을 이용한 block hash와 block header정보의 block_hash 값이 다릅니다. txid를 다시 확인하세요.")

        # print("정상적으로 처리되었습니다.")
    def get_dataframe(self):
        return self.result_df

    def magicbyte_check(self, block):
        if block.magic_byte == "f9beb4d9":
            return True
        else:
            return False

    def size_check(self, size, block):
        if size == block.get_size():
            return True
        else:
            return False

    def merkleroot_check(self, block):
        if block.block_header.merkle_root == block.calculated_merkle_root:
            return True
        else:
            return False

    def hash_value_check(self, block):
        if block.block_hash == block.calculated_block_hash:
            return True
        else:
            return False

    def _binary_file_to_hexadecimal_string_parsing(self, file_path):
        with open(file_path, 'rb') as dax_file:
            data = dax_file.read()
            hexadecimal_binary = binascii.hexlify(data)
        return hexadecimal_binary.decode('utf-8')