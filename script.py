from util import common_util
import ECDSA


opcodes = {
    0x00 : 'OP_0',
    0x4c : 'OP_PUSHDATA1',
    0x4d : 'OP_PUSHDATA2',
    0x4e : 'OP_PUSHDATA4',
    0x4f : 'OP_1NEGATE',
    0x50 : 'OP_RESERVED',
    0x51 : 'OP_1',
    0x52 : 'OP_2',
    0x53 : 'OP_3',
    0x54 : 'OP_4',
    0x55 : 'OP_5',
    0x56 : 'OP_6',
    0x57 : 'OP_7',
    0x58 : 'OP_8',
    0x59 : 'OP_9',
    0x5a : 'OP_10',
    0x5b : 'OP_11',
    0x5c : 'OP_12',
    0x5d : 'OP_13',
    0x5e : 'OP_14',
    0x5f : 'OP_15',
    0x60 : 'OP_16',
    0x61 : 'OP_NOP',
    0x62 : 'OP_VER',
    0x63 : 'OP_IF',
    0x64 : 'OP_NOTIF',
    0x65 : 'OP_VERIF',
    0x66 : 'OP_VERNOTIF',
    0x67 : 'OP_ELSE',
    0x68 : 'OP_ENDIF',
    0x69 : 'OP_VERIFY',
    0x6a : 'OP_RETURN',
    0x6b : 'OP_TOALTSTACK',
    0x6c : 'OP_FROMALTSTACK',
    0x6d : 'OP_2DROP',
    0x6e : 'OP_2DUP',
    0x6f : 'OP_3DUP',
    0x70 : 'OP_2OVER',
    0x71 : 'OP_2ROT',
    0x72 : 'OP_2SWAP',
    0x73 : 'OP_IFDUP',
    0x74 : 'OP_DEPTH',
    0x75 : 'OP_DROP',
    0x76 : 'OP_DUP',
    0x77 : 'OP_NIP',
    0x78 : 'OP_OVER',
    0x79 : 'OP_PICK',
    0x7a : 'OP_ROLL',
    0x7b : 'OP_ROT',
    0x7c : 'OP_SWAP',
    0x7d : 'OP_TUCK',
    0x7e : 'OP_CAT',
    0x7f : 'OP_SUBSTR',
    0x80 : 'OP_LEFT',
    0x81 : 'OP_RIGHT',
    0x82 : 'OP_SIZE',
    0x83 : 'OP_INVERT',
    0x84 : 'OP_AND',
    0x85 : 'OP_OR',
    0x86 : 'OP_XOR',
    0x87 : 'OP_EQUAL',
    0x88 : 'OP_EQUALVERIFY',
    0x89 : 'OP_RESERVED1',
    0x8a : 'OP_RESERVED2',
    0x8b : 'OP_1ADD',
    0x8c : 'OP_1SUB',
    0x8d : 'OP_2MUL',
    0x8e : 'OP_2DIV',
    0x8f : 'OP_NEGATE',
    0x90 : 'OP_ABS',
    0x91 : 'OP_NOT',
    0x92 : 'OP_0NOTEQUAL',
    0x93 : 'OP_ADD',
    0x94 : 'OP_SUB',
    0x95 : 'OP_MUL',
    0x96 : 'OP_DIV',
    0x97 : 'OP_MOD',
    0x98 : 'OP_LSHIFT',
    0x99 : 'OP_RSHIFT',
    0x9a : 'OP_BOOLAND',
    0x9b : 'OP_BOOLOR',
    0x9c : 'OP_NUMEQUAL',
    0x9d : 'OP_NUMEQUALVERIFY',
    0x9e : 'OP_NUMNOTEQUAL',
    0x9f : 'OP_LESSTHAN',
    0xa0 : 'OP_GREATERTHAN',
    0xa1 : 'OP_LESSTHANOREQUAL',
    0xa2 : 'OP_GREATERTHANOREQUAL',
    0xa3 : 'OP_MIN',
    0xa4 : 'OP_MAX',
    0xa5 : 'OP_WITHIN',
    0xa6 : 'OP_RIPEMD160',
    0xa7 : 'OP_SHA1',
    0xa8 : 'OP_SHA256',
    0xa9 : 'OP_HASH160',
    0xaa : 'OP_HASH256',
    0xab : 'OP_CODESEPARATOR',
    0xac : 'OP_CHECKSIG',
    0xad : 'OP_CHECKSIGVERIFY',
    0xae : 'OP_CHECKMULTISIG',
    0xaf : 'OP_CHECKMULTISIGVERIFY',
    0xb0 : 'OP_NOP1',
    0xb1 : 'OP_CHECKLOCKTIMEVERIFY',
    0xb2 : 'OP_CHECKSEQUENCEVERIFY',
    0xb3 : 'OP_NOP4',
    0xb4 : 'OP_NOP5',
    0xb5 : 'OP_NOP6',
    0xb6 : 'OP_NOP7',
    0xb7 : 'OP_NOP8',
    0xb8 : 'OP_NOP9',
    0xb9 : 'OP_NOP10',
    0xff : 'OP_INVALIDOPCODE',
}


# 0 - Having a private ECDSA key
#    18e14a7b6a307f426a94f8114701e7c8e774e7f9a47e2c2035db29a206321725

# 1 - Take the corresponding public key generated with it (33 bytes, 1 byte 0x02 (y-coord is even), and 32 bytes corresponding to X coordinate)
#    0250863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b2352

# 2 - Perform SHA-256 hashing on the public key
#    0b7c28c9b7290c98d7438e70b3d3f7c848fbd7d1dc194ff83f4f7cc9b1378e98

# 3 - Perform RIPEMD-160 hashing on the result of SHA-256
#    f54a5851e9372b87810a8e60cdd2e7cfd80b6e31
#    270af53a1ba880c52aa858aa12523706d298792e

# 4 - Add version byte in front of RIPEMD-160 hash (0x00 for Main Network)
#    00f54a5851e9372b87810a8e60cdd2e7cfd80b6e31

# 00270af53a1ba880c52aa858aa12523706d298792e
# (note that below steps are the Base58Check encoding, which has multiple library options available implementing it)

# 5 - Perform SHA-256 hash on the extended RIPEMD-160 result
#    ad3c854da227c7e99c4abfad4ea41d71311160df2e415e713318c70d67c6b41c

# 6 - Perform SHA-256 hash on the result of the previous SHA-256 hash
#    c7f18fe8fcbed6396741e58ad259b5cb16b7fd7f041904147ba1dcffabf747fd
# 7 - Take the first 4 bytes of the second SHA-256 hash. This is the address checksum

#    c7f18fe8
# 8 - Add the 4 checksum bytes from stage 7 at the end of extended RIPEMD-160 hash from stage 4. This is the 25-byte binary Bitcoin Address.

#    00f54a5851e9372b87810a8e60cdd2e7cfd80b6e31c7f18fe8
# 9 - Convert the result from a byte string into a base58 string using Base58Check encoding. This is the most commonly used Bitcoin Address format




"""
    Pay to Public key hash 0x00 1
    pay to Public key 0x00 1
    
    Pay-to-Script-Hash Address 0x05 3

    script 종류
    pay to Public Key Hash : P2PKH (3번부터 시작) (33바이트)
        prefix : 00
        to address : base58_encode('00' + {Public key hash} + double_sha256('00' + {Public key hash})[:8])

    pay to Script Hash : P2SH (3번부터 시작)
        prefix : 00
        to address : base58_encode('05' + {Public key hash} + double_sha256('05' + {Public key hash})[:8])


    pay to Public Key : P2PK(65바이트)
        public key : prefix 04 인경우 길이 64바이트 + 1바이트(prefix) -> COMPRESS -> 1번 -> SHA256 -> RIPEMD-160
        prefix : 00
        to address : base58_encode('00' + {Public key})



    # https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki#witness-program
    # https://github.com/mcdallas/cryptotools/blob/master/btctools/address.py
    pay to witness script hash
        bech32 encoding
        bech32(version + pubkey hash) 

    pay to witness public key hash
        bech32 encoding
        bech32(version + pubkey hash)

    Nonetransaction

    None standard     

    output의 pubkey script만을 분석함.

    Pay to Public key Hash : OP_DUP OP_HASH160 DATA_LENGTH <PUBLICKEYHASH> OP_EQUALVERIFY OP_CHECKSIG 
    Pay to Script Key Hash : OP_HASH160 DATA_LENGTH <PUBLICK KEY HASH> OP_EQUAL
    Pay to Public Key : data_length <public key> OP_CHECK_SIG

    public key hash / public key는 prefix가 00
    script hash / prefix가 05

    
    
    
    segwit : OP_0 data_length <pubkey_hash>
        data-length: 20(), 3


hrp: the human-readable part. This is bc for mainnet and tb for testnet
witver: the witness version. This is 0 at the moment represented by the byte 0x00 but it can go up to 16 when they add more versions.
witprog: the witness programm. 
    In case you want a Pay-to-witness-public-key (P2WPK) address which is the most common ones, 
    this is the 20-byte hash160 of the compressed public key i.e ripemd160(sha256(compressed_pub_key)). 
    In case you want a Pay-to-witness-script-hash (P2WSH) address, 
    this is the 32-byte sha256 of the scriptPubKey which is the script that will need to evaluate to True for someone to be able to spend the output. 
    More on this in BIP141


    NULL DATA : OP_RETURN
    None standard : 그외


https://www.blockchain.com/btc/tx/b300ab73950a68e0845e7f5ebd2cc6857308c02f65d5725b01cc70d3ab1749c5 segwit 인데 output이 1, 3임.

address의 Prefix에는 3가지 종류가 있음.

<hex>


04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f

62e907b15cbf27d5425399ebf6f0fb50ebb88f18


<base58>
1 : 
3 :
bc1 :





    'utxo_url': 'https://blockchain.info/unspent?active={address}',
"""

class script:

    def __init__(self, byte_array):
        self.hex_byte = byte_array
        self.common_util = common_util
        self.raw_script, self.parsed_script = self.parsing_script(byte_array)
        
    def parsing_script(self, hex_byte):
        data_length = int(len(hex_byte) / 2)
        offset = 0
        raw_script = [] 
        parsed_script = []
        
        while data_length > offset:
            one_byte, offset = self.common_util.slicing_and_get_offset(hex_byte, offset, 1)
            code = self.common_util.big_endian_to_little_endian_number(one_byte)
            if code in opcodes:
                raw_script.append(one_byte)
                parsed_script.append(opcodes[code])
            else:
                push_data, offset = self.common_util.slicing_and_get_offset(hex_byte, offset, code)
                parsed_script.append(f"data_length : {code}")
                parsed_script.append(push_data)
                raw_script.append(one_byte)
                raw_script.append(push_data)

        return (raw_script, parsed_script)

        # return (" ".join(raw_script), " ".join(parsed_script))

    def get_dict(self):
        return {
            "raw_script" : self.raw_script,
            "parsed_script" : self.parsed_script,
        }