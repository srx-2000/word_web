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
        # cursor.execute("drop database if exists " + self.db_name)
        create_db_sql = "Create Database If Not Exists " + self.db_name
        cursor.execute(create_db_sql)
        use_db_sql = "use " + self.db_name
        cursor.execute(use_db_sql)
        # cursor.execute("drop table if exists `user`")
        # cursor.execute("drop table if exists `word`")
        create_table_sql1 = """
        CREATE TABLE if not exists `user`(
            id INT PRIMARY KEY AUTO_INCREMENT COMMENT "用户id",
            uid VARCHAR(36) NOT NULL UNIQUE COMMENT "用户uuid",
            username VARCHAR(81) NOT NULL COMMENT "用户名",
            `password` VARCHAR(255) NOT NULL COMMENT "用户密码"
        ) ENGINE=INNODB DEFAULT CHARSET utf8 COMMENT = "用户表";
        """
        create_table_sql2 = """
        CREATE TABLE if not exists `word`(
            word_uid INT PRIMARY KEY AUTO_INCREMENT COMMENT "单词id",
            user_uid VARCHAR(36) NOT NULL COMMENT "用户uid",
            word VARCHAR(81) NOT NULL COMMENT "单词英文",
            mean VARCHAR(255) NOT NULL COMMENT "单词中文意思",
            memory_way VARCHAR(255) COMMENT "单词记忆方法，对应百度翻译词根，可为空",
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
    def insert_word(self, user_uid, word, mean, memory_way, year, month, day):
        db = self.__get_connect()
        cursor = db.cursor()
        sql = "insert into `word`(user_uid,word,mean,memory_way,`year`,`month`,`day`) values " \
              "('{user_uid}','{word}','{mean}','{memory_way}','{year}','{month}','{day}')" \
            .format(user_uid=user_uid, word=word, mean=mean, memory_way=memory_way, year=year, month=month, day=day)
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

    # 更新一个单词
    def update_word(self, word_id, user_uid, word, mean, memory_way):
        db = self.__get_connect()
        cursor = db.cursor()
        sql = f"UPDATE `word` SET word='{word}',mean='{mean}',memory_way='{memory_way}' WHERE word_uid='{word_id}' AND user_uid='{user_uid}'"
        try:
            result = cursor.execute(sql)
            db.commit()
            return result
        except Exception as e:
            db.rollback()
        finally:
            db.close()

    # 删除一个单词
    def delete_single_word(self, word_id, word, mean, memory_way, user_uuid, year, month, day):
        db = self.__get_connect()
        cursor = db.cursor()
        sql = f"UPDATE word SET `status`='-1' WHERE word_uid='{word_id}'"
        cursor.execute(sql)
        db.commit()
        # 查看更新后的结果
        data = self.select_single_word(word, mean, memory_way, user_uuid, year, month, day)
        try:
            if data != None:
                if data[-1] == -1:
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

    def search_word(self, user_uuid, word_prefix, prefix_type, status=1):
        db = self.__get_connect()
        cursor = db.cursor()
        if prefix_type == 1:
            sql = f"select * from `word` where user_uid='{user_uuid}' and status='{status}' and word like '%{word_prefix}%'"
        else:
            sql = f"select * from `word` where user_uid='{user_uuid}' and status='{status}' and mean like '%{word_prefix}%'"
        cursor.execute(sql)
        data = cursor.fetchall()
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
    def select_single_word(self, word, mean, memory_way, user_uuid, year, month, day):
        db = self.__get_connect()
        cursor = db.cursor()
        sql = "select * from `word` where user_uid='{user_uuid}' and word='{word}' " \
              "and mean='{mean}' and `memory_way` ='{memory_way}' and `year` ='{year}'and `month` ='{month}" \
              "'and `day` ='{day}'".format(word=word,
                                           mean=mean,
                                           year=year,
                                           month=month,
                                           day=day,
                                           memory_way=memory_way,
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
    def select_word_by_date(self, uuid, page, page_size, year=None, month=None, day=None, status=1):
        db = self.__get_connect()
        cursor = db.cursor()
        # page_size = 30
        begin = page_size * page
        sql = "select * from `word` where user_uid='{uuid}'".format(uuid=uuid)
        sql = sql + f" and `status` = {status}"
        try:
            if year != None:
                sql = sql + " and `year`=" + year
                if month != None:
                    sql = sql + " and `month`=" + month
                    if day != None:
                        sql = sql + " and `day`=" + day
                sql = sql + " LIMIT {begin},{pageSize}".format(begin=begin, pageSize=page_size)
                cursor.execute(sql)
                data = cursor.fetchall()
                return data
            else:
                sql = sql + " LIMIT {begin},{pageSize}".format(begin=begin, pageSize=page_size)
                cursor.execute(sql)
                data = cursor.fetchall()
                return data
        finally:
            db.close()

    # 查询用户单词数量
    def query_count(self, uuid, year=None, month=None, day=None, status=1):
        db = self.__get_connect()
        cursor = db.cursor()
        sql = "select count(*) from `word` where user_uid='{uuid}'".format(uuid=uuid)
        sql = sql + f" and `status` = {status}"
        try:
            if year != None:
                sql = sql + " and `year`=" + year
                if month != None:
                    sql = sql + " and `month`=" + month
                    if day != None:
                        sql = sql + " and `day`=" + day
                cursor.execute(sql)
                data = cursor.fetchone()
                return data
            else:
                cursor.execute(sql)
                data = cursor.fetchone()
                return data
        finally:
            db.close()

    def is_username_exist(self, username):
        db = self.__get_connect()
        cursor = db.cursor()
        sql = "select * from `user` where username='{username}'".format(username=username)
        cursor.execute(sql)
        data = cursor.fetchone()
        db.close()
        if data == None:
            return False
        else:
            return True

    def get_high_frequency(self, user_id):
        db = self.__get_connect()
        cursor = db.cursor()
        sql = f"SELECT word,mean,memory_way,COUNT(*) AS count_num FROM word WHERE `status`=1 AND user_uid='{user_id}' GROUP BY word,mean,memory_way HAVING count_num>1 ORDER BY count_num DESC"
        cursor.execute(sql)
        data = cursor.fetchall()
        db.close()
        return data
