import os
import sys
import glob
import binascii

from default_logger import defaultLogger
from bitcoin_batch import bitcoinBatch

import pandas as pd

result_column = ["Filename", "BlockHash", "PreviousBlockHash","TransactionCnt", "Description"]

def main():
    file_list = glob.glob(os.path.join(os.getcwd(), "dat","*.dat"))
    logger_class = defaultLogger()


    # csv 파일에 .dat file을 읽은 기록을 남김
"""
    ["Filename", "BlockHash", "PreviousBlockHash","TransactionCnt", "Description"]
    이미 읽고 기록한 파일을 읽지 않기위해서 로깅.
"""


    # if len(sys.argv) != 2:
    #     raise ValueError("엑셀 경로를 입력하세요.")
    
    # csv_file_path = sys.argv[1] 
    # df_dataframe = pd.read_csv(filepath_or_buffer=csv_file_path, header=0)

    # download_file_list = list(df_dataframe["Filename"][~df_dataframe["Filename"].duplicated(keep='first')])


    for file_path in file_list:
        # file_name = file_path.split('\\')[-1]
        # if file_name in download_file_list:
        #     continue

        bitcoin_ = bitcoinBatch(file_path, logger_class)
        # parsing_result_df = bitcoin_.get_dataframe()
        # df_dataframe = df_dataframe.append(parsing_result_df)

        # # 파일을 지워주고 다시 생성해준다.
        # os.remove(csv_file_path)
        # df_dataframe.to_csv(path_or_buf=csv_file_path, header=True, index=False)

if __name__ == "__main__":
    main()


    