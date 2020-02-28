from util import common_util
from util import unhexlify
from script import script

"""
Transaction structure

ytes	Name	Data Type	Description
4/	version/	uint32_t/	Transaction version number; currently version 1 or 2. Programs creating transactions using newer consensus rules may use higher version numbers. Version 2 means that BIP 68 applies.
Varies/	tx_in/ count/	compactSize uint	Number of inputs in this transaction.
Varies/	tx_in/	txIn/	Transaction inputs. See description of txIn below.
Varies/	tx_out/ count/	compactSize uint	Number of outputs in this transaction.
Varies/	tx_out/	txOut/	Transaction outputs. See description of txOut below.
4/	lock_time/	uint32_t/	A time (Unix epoch time) or block number. See the locktime parsing rules.

txid를 구하는 법 : transaction byte array 전체를 double sha 256을 통해서 해쉬한다.

segwit : https://github.com/bitcoin/bips/blob/master/bip-0144.mediawiki

Field Size Name Type Description 
4 version int32_t Transaction data format version 
1 marker char Must be zero 
1 flag char Must be nonzero 
1+ txin_count var_int Number of transaction inputs 
41+ txins txin[] A list of one or more transaction inputs 
1+ txout_count var_int Number of transaction outputs 
9+ txouts txouts[] A list of one or more transaction outputs 
1+ script_witnesses script_witnesses[] The witness structure as a serialized byte array 
4 lock_time uint32_t The block number or timestamp until which the transaction is locked 
"""

class transaction:
    def __init__(self, byte_array):
        self.common_util = common_util
        # self.original_byte = byte_array
    
        offset = 0
        
        self.version, offset= self.common_util.slicing_and_get_offset(byte_array, offset, 4)

        self.isSegwit = self.check_segwit(self.common_util.slicing(byte_array, offset, 2))

        # segwit인 경우에는 marker와 flag를 추가해준다.
        if self.isSegwit:
            self.marker, offset= self.common_util.slicing_and_get_offset(byte_array, offset, 1)
            self.flag, offset = self.common_util.slicing_and_get_offset(byte_array, offset, 1)

        self.input_count, input_byte = self.common_util.get_compact_size(self.common_util.slicing(byte_array, offset ,9))
        
        offset += input_byte

        # input count만큼 input transactions가 생성됨.
        self.input_transactions = self._parsing_input_transactions(self.common_util.get_all_bytes(byte_array, offset), self.input_count)

        self.isCoinbase = self.check_coinbase()

        offset += self._get_list_element_size(self.input_transactions)
        self.output_count, output_byte = self.common_util.get_compact_size(self.common_util.slicing(byte_array, offset ,9))

        offset += output_byte

        # outuput count만큼 output transactions가 생성됨
        self.output_transactions = self._parsing_output_transactions(self.common_util.get_all_bytes(byte_array, offset), self.output_count)
        offset += self._get_list_element_size(self.output_transactions)

        
        if self.isSegwit:
            self.offset_before_segwit = offset
            offset = self.parsing_segwit(byte_array, offset)

        # lock time 얻기

        self.lock_time, offset = self.common_util.slicing_and_get_offset(byte_array, offset, 4)

        self.offset = offset

        self.transaction_id = self.common_util.double_hash(unhexlify(self.parsing_transaction_id(byte_array)))

    def parsing_transaction_id(self, byte_array):
        if self.isSegwit:
            hex_string = self.version + self.common_util.slicing(byte_array,6, self.offset_before_segwit - 6) + self.lock_time
        else:
            hex_string = self.common_util.slicing(byte_array, 0, self.offset)
        return hex_string

    def parsing_segwit(self, byte_array, offset):
        # 각 input tx 마다 witness가 여러개 붙어있을 수 있음.
        for txin in self.input_transactions:
            witness_cnt, byte_size = self.common_util.get_compact_size(self.common_util.slicing(byte_array,offset, 9))
            offset += byte_size
            for j in range(witness_cnt):
                witness_byte_length, byte_size = self.common_util.get_compact_size(self.common_util.slicing(byte_array,offset, 9))
                offset += byte_size
                segwit_script, offset = self.common_util.slicing_and_get_offset(byte_array, offset, witness_byte_length)
                txin.append_segwit(segwit_script)        

        return offset

    def check_coinbase(self):
        for intx in self.input_transactions:
            if intx.isCoinbase:
                return True
        
        return False

    def __str__(self):
        return f"""
            version : {str(self.common_util.parsing_to_uint32_t(self.version))}
            tx_in_cnt :{str(self.input_count)}
            tx_in : 
                {str(self._get_list_string(self.input_transactions))}
            tx_out_cnt : {str(self.output_count)}
            tx_out :
                {str(self._get_list_string(self.output_transactions))}
        """
    def check_segwit(self, data):
        if data[:] == '0001':
            return True
        else:
            return False
    
    def get_dict(self):
        return {
            "version" : self.common_util.parsing_to_uint32_t(self.version),
            # "tx_in_cnt" : self.input_count,
            # "tx_in" : self._get_list_dict(self.input_transactions),
            "tx_out_cnt" : self.output_count,
            "tx_out" : self._get_list_dict(self.output_transactions),
            "txid" : self.common_util.big_endian_to_little_endian(self.transaction_id),
            # "locktime" : self.common_util.parsing_to_uint32_t(self.lock_time),
            "isSegwit" : self.isSegwit,
        }

    def get_size(self):
        return self.offset


    def _get_list_element_size(self, transaction_list):
        size = 0
        for transaction in transaction_list:
            size += transaction.get_size()
        return size

    def _parsing_output_transactions(self, byte_array, count):
        output_transaction_list = []
        data_from = 0

        for i in range(count):
            output_transaction = outputTransaction(self.common_util.get_all_bytes(byte_array, data_from))
            data_from += output_transaction.get_size()
            output_transaction_list.append(output_transaction)
        
        return output_transaction_list

    def _parsing_input_transactions(self, byte_array, count):
        input_transaction_list = []
        data_from = 0

        for i in range(count):
            input_transaction = inputTransaction(self.common_util.get_all_bytes(byte_array, data_from))
            data_from += input_transaction.get_size()
            input_transaction_list.append(input_transaction)

        return input_transaction_list

    def _get_list_string(self, obj_list):
        expression = ""
        for obj in obj_list:
            expression += str(obj)

        return expression

    def _get_list_dict(self, obj_list):
        dict_list = []
        for obj in obj_list:
            dict_list.append(obj.get_dict())
        
        return dict_list

"""
        txIn(transaction input)
        Bytes	Name	Data Type	Description
        32/	previous_output/	outpoint/	The previous outpoint being spent. See description of outpoint below.
        4 / index	/uint32_t
        Varies/	script/ bytes/	compactSize uint	The number of bytes in the signature script. Maximum is 10,000 bytes.
        Varies/	signature/ script/	char[]	A script-language script which satisfies the conditions placed in the outpoint’s pubkey script. Should only contain data pushes; see the signature script modification warning.
        4/	sequence/	uint32_t/	Sequence number. Default for Bitcoin Core and almost all other programs is 0xffffffff.


    <coin_base>
        Bytes	Name	Data Type	Description
        32	hash (null)	char[32]	A 32-byte null, as a coinbase has no previous outpoint.
        4	index (UINT32_MAX)	uint32_t	0xffffffff, as a coinbase has no previous outpoint.
        Varies	script bytes	compactSize uint	The number of bytes in the coinbase script, up to a maximum of 100 bytes.
        Varies (4)	height	script	The block height of this block as required by BIP34. Uses script language: starts with a data-pushing opcode that indicates how many bytes to push to the stack followed by the block height as a little-endian unsigned integer. This script must be as short as possible, otherwise it may be rejected.

        The data-pushing opcode will be 0x03 and the total size four bytes until block 16,777,216 about 300 years from now.
        Varies	coinbase script	None	The coinbase field: Arbitrary data not exceeding 100 bytes minus the (4) height bytes. Miners commonly place an extra nonce in this field to update the block header merkle root during hashing.
        4	sequence	uint32_t	Sequence number.
"""


class inputTransaction:


    def __init__(self, byte_array):
        self.common_util = common_util
        # self.original_byte_array = byte_array

        offset = 0
        self.previous_output_hash, offset = self.common_util.slicing_and_get_offset(byte_array, offset, 32)

        # coin base 체크
        self.previous_output_hash_index, offset = self. common_util.slicing_and_get_offset(byte_array, offset, 4)
        self.script_size, script_byte_size = self.common_util.get_compact_size(self.common_util.slicing(byte_array, offset, 9))
        
        offset = offset + script_byte_size

        self.script, offset = self.common_util.slicing_and_get_offset(byte_array, offset, self.script_size)
        self.sequence, offset = self.common_util.slicing_and_get_offset(byte_array, offset, 4)

        self.offset = offset
        self.isCoinbase = self.check_coinbase(self.previous_output_hash)

        self.parsed_script = script(self.script)

        self.segwit = []

        # print(self.offset)
    def append_segwit(self, segwit):
        self.segwit.append(segwit)

    def get_size(self):
        return self.offset
    
    # def get_hex_string(self):
    #     return self.common_util.slicing(self.original_byte_array, 0, self.offset)

    def _parsing_script(self, byte_array):
        script_dict = {}
        offset = 0
        op_cnt = 0
        hash_cnt = 0
        while not self._check_end(byte_array, offset):
            one_byte, offset = self.common_util.slicing_and_get_offset(byte_array, offset, 1)
            code = self.common_util.big_endian(one_byte)
            if code > 0x4b:
                hash_value, offset = self.common_util.slicing_and_get_offset(byte_array, offset, code)
                script_dict[f"hash_{str(hash_cnt)}"] = {}
                script_dict[f"hash_{str(hash_cnt)}"]["value"] = hash_value
                script_dict[f"hash_{str(hash_cnt)}"]["length"] = code
                hash_cnt += 1
            else:
                script_dict[f"opcode_{str(op_cnt)}"] = one_byte
                op_cnt += 1
            
            # print(script_dict)

        # print(script_dict)
        return script_dict, offset

    def _check_end(self, byte_array, start_index):
        return True if self.common_util.slicing(byte_array, start_index, 4) == "ffffffff" else False


    def check_coinbase(self, previous_txid):
        if previous_txid == "0" * 64:
            # print(f"coinbase sequence : {self.common_util.parsing_to_uint32_t(self.sequence)}")
            return True
        else:
            return False
    
    def __str__(self):
        return f"""
                previous_output : {str(self.common_util.big_endian_to_little_endian(self.previous_output_hash))}
                index : {str(self.common_util.parsing_to_uint32_t(self.previous_output_hash_index))}
                script_size : {str(self.script_size)} 
                signature : {str(self.script)}
                sequence : {str(self.common_util.parsing_to_int32_t(self.sequence))}
        """

    def get_dict(self):
        return {
            "previous_output" : self.common_util.big_endian_to_little_endian(self.previous_output_hash),
            "index" : self.common_util.parsing_to_uint32_t(self.previous_output_hash_index),
            "script_size" : self.script_size,
            "signature" : self.script,
            "sequence" : self.common_util.parsing_to_uint32_t(self.sequence),
            "parsed_script" : self.parsed_script.get_dict(),
        }

    """
    TxOut
    Bytes	Name	Data Type	Description
    8	value	int64_t	Number of satoshis to spend. May be zero; the sum of all outputs may not exceed the sum of satoshis previously spent to the outpoints provided in the input section. (Exception: coinbase transactions spend the block subsidy and collected transaction fees.)
    1+	pk_script bytes	compactSize uint	Number of bytes in the pubkey script. Maximum is 10,000 bytes.
    Varies	pk_script	char[]	Defines the conditions which must be satisfied to spend this output.
    """
class outputTransaction:
    def __init__(self, byte_array):
        # self.original_byte = byte_array
        self.common_util = common_util
        offset = 0
        self.value, offset = self.common_util.slicing_and_get_offset(byte_array, offset, 8)
        self.byte_size, byte_offset = self.common_util.get_compact_size(self.common_util.slicing(byte_array, offset, 9))
        offset = offset + byte_offset
        self.script, offset = self.common_util.slicing_and_get_offset(byte_array, offset, self.byte_size)
        self.offset = offset
        self.parsed_script = script(self.script)
        
        # type의 종류 
        """
        Pay to Public key hash 
        Pay to Public key 
        Pay to Script Hash
        Pay to Witness Public key hash : version 0 / byte : 20
        Pay to Witness Script hash : version 0 / byte : 32
        None Transaction : OP_RETURN 
        """

    def get_size(self):
        return self.offset

    # def get_hex_string(self):
    #     return self.common_util.slicing(self.original_byte, 0, self.offset)

    def __str__(self):
        return f"""
                value : {str(self.common_util.parsing_to_int64_t(self.value))}
                script_size : {str(self.byte_size)}
                script : {str(self.script)}
        """

    def parsing_address(self, script):
        operation_list = script.parsed_script
        pass

    def get_pushed_data(self, ):
        pass

    def check_data_type(self, data):
        pass
        
    def get_dict(self):
        return {
            "value" : self.common_util.parsing_to_int64_t(self.value),
            "script_size" : self.byte_size,
            "script" : self.script,
            "parsed_script" : self.parsed_script.get_dict(),
        }
