import os

import yaml

app_path = os.path.dirname(os.path.dirname(__file__))


class Config_loader:
    __root_path = ""
    __db_host = ""
    __db_port = ""
    __db_name = ""
    __db_username = ""
    __db_password = ""
    __server_host = ""
    __server_port = ""
    __appid = ""
    __key = ""

    def __init__(self):
        config = open(app_path + os.sep + "config.yaml", mode="r", encoding="utf-8")
        cfg = config.read()
        yaml_line = yaml.load(stream=cfg, Loader=yaml.FullLoader)
        self.__db_host = yaml_line["db_host"]
        self.__db_port = yaml_line["db_port"]
        self.__db_name = yaml_line["db_name"]
        self.__db_username = yaml_line["db_username"]
        self.__db_password = yaml_line["db_password"]
        self.__server_host = yaml_line["server_host"]
        self.__server_port = yaml_line["server_port"]
        self.__appid = yaml_line["appid"]
        self.__key = yaml_line["key"]

    def get_root_path(self):
        return self.__root_path

    def get_db_host(self):
        return self.__db_host

    def get_api_appid(self):
        return self.__appid

    def get_api_key(self):
        return self.__key

    def get_db_port(self):
        return self.__db_port

    def get_db_name(self):
        return self.__db_name

    def get_db_password(self):
        return self.__db_password

    def get_db_username(self):
        return self.__db_username

    def get_server_host(self):
        return str(self.__server_host)

    def get_server_port(self):
        return str(self.__server_port)
