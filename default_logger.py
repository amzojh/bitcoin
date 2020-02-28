import logging
import os
import datetime


class defaultLogger():
    def __init__(self, name="bitcoin_logger"):
        self.logger = logging.getLogger(name)
        self._set_default_log_conf()

    def get_logger(self):
        return self.logger

    def set_error_message(self, error, file_name, block_info):
        return f"""
    오류명 : {error}
    파일명 : {file_name}
    블록정보 :
        {block_info}
        """
        
    def _set_default_log_conf(self, filepath=None):
        
        file_path = os.getcwd() + '/log'
        # print(file_path)

        if filepath is not None:
            file_path = filepath

        if not os.path.exists(file_path):
            os.makedirs(file_path)

        file_formatter = logging.Formatter(fmt='{asctime} - [{levelname}] {message}', style='{')
        stream_formatter = logging.Formatter(fmt='{message}', style='{')

        filename = os.path.join(os.path.dirname(file_path) + '/log', datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S.log'))
        file_handler = logging.FileHandler(filename, 'w')
        stream_handler = logging.StreamHandler()

        file_handler.setFormatter(file_formatter)
        stream_handler.setFormatter(stream_formatter)

        self.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        stream_handler.setLevel(logging.INFO)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)
