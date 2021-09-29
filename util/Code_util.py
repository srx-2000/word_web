import time
import hashlib
import uuid

class Code_util:
    file_name=""

    def encode(self,file_name):
        if file_name!=None and file_name.strip()!="":
            name_list=file_name.split(".")
            code=(name_list[0]+str(time.time())).encode(encoding='utf-8')
            result=hashlib.md5(code).hexdigest()+"."+name_list[-1]
            return (result,True)
        else:
            return (None,False)

    def get_uuid(self):
        print(uuid.uuid1())
        return uuid.uuid1()


