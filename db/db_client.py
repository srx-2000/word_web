import pymysql
from util.Config_loader import Config_loader


class db_client():
    host = ""
    port = ""
    db_name = ""
    db_username = ""
    db_password = ""
    loader = Config_loader()

    def __init__(self):
        self.host = self.loader.get_db_host()
        self.port = self.loader.get_db_port()
        self.db_name = self.loader.get_db_name()
        self.db_username = self.loader.get_db_username()
        self.db_password = self.loader.get_db_password()

    def __get_connect(self):
        db = pymysql.connect(host=self.host, port=self.port, user=self.db_username, passwd=self.db_password,
                             charset='utf8')
        cursor = db.cursor()
        use_db_sql = "use " + self.db_name
        cursor.execute(use_db_sql)
        return db

    def init_db(self):
        db = pymysql.connect(host=self.host, port=self.port, user=self.db_username, passwd=self.db_password,
                             charset='utf8')
        cursor = db.cursor()
        cursor.execute("drop database if exists " + self.db_name)
        create_db_sql = "create database " + self.db_name
        cursor.execute(create_db_sql)
        use_db_sql = "use " + self.db_name
        cursor.execute(use_db_sql)
        cursor.execute("drop table if exists `user`")
        cursor.execute("drop table if exists `word`")
        create_table_sql1 = """
        CREATE TABLE `user`(
            id INT PRIMARY KEY AUTO_INCREMENT COMMENT "用户id",
            uid VARCHAR(36) NOT NULL UNIQUE COMMENT "用户uuid",
            username VARCHAR(81) NOT NULL COMMENT "用户名",
            `password` VARCHAR(255) NOT NULL COMMENT "用户密码"
        ) ENGINE=INNODB DEFAULT CHARSET utf8 COMMENT = "用户表";
        """
        create_table_sql2 = """
        CREATE TABLE `word`(
            word_uid INT PRIMARY KEY AUTO_INCREMENT COMMENT "单词id",
            user_uid VARCHAR(36) NOT NULL COMMENT "用户uid",
            word VARCHAR(81) NOT NULL COMMENT "单词英文",
            mean VARCHAR(255) NOT NULL COMMENT "单词中文意思",
            `year` INT NOT NULL COMMENT "单词存储年份",
            `month` INT NOT NULL COMMENT "单词存储月份",
            `day` INT NOT NULL COMMENT "单词存储日份",
            `status` TINYINT NOT NULL DEFAULT 1 COMMENT "单词状态，默认为1,删除为-1"
        ) ENGINE=INNODB DEFAULT CHARSET utf8 COMMENT = '单词表';
        """
        cursor.execute(create_table_sql1)
        cursor.execute(create_table_sql2)
        db.close()

    # 插入一个用户
    def insert_user(self, username, password, user_uuid):
        db = self.__get_connect()
        cursor = db.cursor()
        sql = "insert into `user`(username,password,uid) values " \
              "('{username}','{password}','{user_uuid}')" \
            .format(username=username, password=password, user_uuid=user_uuid)
        # sql = sql.replace("\\", "\\\\")
        cursor.execute(sql)
        db.commit()
        data = self.select_single_user_by_id(user_uuid)
        try:
            if data != None:
                return True
            else:
                return False
        finally:
            db.close()

    # 插入一个单词
    def insert_word(self, user_uid, word, mean, year, month, day):
        db = self.__get_connect()
        cursor = db.cursor()
        sql = "insert into `word`(user_uid,word,mean,`year`,`month`,`day`) values " \
              "('{user_uid}','{word}','{mean}','{year}','{month}','{day}')" \
            .format(user_uid=user_uid, word=word, mean=mean, year=year, month=month, day=day)
        cursor.execute(sql)
        word_id = cursor.lastrowid
        db.commit()
        data = self.select_single_word_id(word_id)
        try:
            if data != None:
                return True
            else:
                return False
        finally:
            db.close()

    # 删除一个单词
    def delete_single_word(self, word, mean, user_uuid, year, month, day):
        db = self.__get_connect()
        cursor = db.cursor()
        sql = 'UPDATE word SET `status`="-1" WHERE word="{word}" AND user_uid="{user_uuid}" AND mean="{mean}"' \
              ' AND `year`="{year}"AND `month`="{month}"AND `day`="{day}"'.format(word=word, user_uuid=user_uuid,
                                                                                  mean=mean, year=year, month=month,
                                                                                  day=day)
        cursor.execute(sql)
        db.commit()
        # 查看更新后的结果
        data = self.select_single_word(word, mean, user_uuid, year, month, day)
        try:
            if data != None:
                if data[-1] != "-1":
                    return True
                else:
                    return False
            else:
                return False
        finally:
            db.close()

    # 通过用户uid查询单个用户，主要作用是在insert_user中用
    def select_single_user_by_id(self, user_uuid):
        db = self.__get_connect()
        cursor = db.cursor()
        sql = "select * from `user` where uid='%s'" % (user_uuid)
        cursor.execute(sql)
        data = cursor.fetchone()
        db.close()
        return data

    # 主要用于登录
    def select_single_user_by_login(self, username, password):
        db = self.__get_connect()
        cursor = db.cursor()
        sql = "select * from `user` where username='{username}' and password='{password}'".format(username=username,
                                                                                                  password=password)
        cursor.execute(sql)
        data = cursor.fetchone()
        db.close()
        return data

    # 通过用户uid查询单个用户的所有单词
    def select_word_by_user_id(self, user_uuid):
        db = self.__get_connect()
        cursor = db.cursor()
        sql = "select * from `user` where uid='%s'" % (user_uuid)
        cursor.execute(sql)
        data = cursor.fetchone()
        db.close()
        return data

    # 查询单个单词
    def select_single_word(self, word, mean, user_uuid, year, month, day):
        db = self.__get_connect()
        cursor = db.cursor()
        sql = "select * from `word` where user_uid='{user_uuid}' and word='{word}' " \
              "and mean='{mean}' and `year` ='{year}'and `month` ='{month}'and `day` ='{day}'".format(word=word,
                                                                                                      mean=mean,
                                                                                                      year=year,
                                                                                                      month=month,
                                                                                                      day=day,
                                                                                                      user_uuid=user_uuid)
        cursor.execute(sql)
        data = cursor.fetchone()
        db.close()
        return data

    # 通过id查询单词
    def select_single_word_id(self, word_id):
        db = self.__get_connect()
        cursor = db.cursor()
        sql = "select * from `word` where word_uid='{word_uid}'".format(word_uid=word_id)
        cursor.execute(sql)
        data = cursor.fetchone()
        db.close()
        return data

    # 根据日期获取单词
    def select_word_by_date(self, uuid, year=None, month=None, day=None):
        db = self.__get_connect()
        cursor = db.cursor()
        sql = "select * from `word` where user_uid='{uuid}'".format(uuid=uuid)
        try:
            if year != None:
                sql = sql + " and `year`=" + year
                if month != None:
                    sql = sql + " and `month`=" + month
                    if day != None:
                        sql = sql + " and `day`=" + day
                cursor.execute(sql)
                data = cursor.fetchall()
                return data
            else:
                cursor.execute(sql)
                data = cursor.fetchall()
                return data
        finally:
            db.close()

    # 查询用户单词数量
    def query_count(self, uuid, year=None, month=None, day=None):
        db = self.__get_connect()
        cursor = db.cursor()
        sql = "select count(*) from `word` where user_uid='{uuid}'".format(uuid=uuid)
        try:
            if year != None:
                sql = sql + " and `year`=" + year
                if month != None:
                    sql = sql + " and `month`=" + month
                    if day != None:
                        sql = sql + " and `day`=" + day
            else:
                cursor.execute(sql)
                data = cursor.fetchone()
                return data
        finally:
            db.close()
