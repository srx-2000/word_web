"""
@ModuleName: test1
@Description: 
@Author: Beier
@Time: 2022/7/18 16:10
"""

import hashlib

import parsel
import requests

from util.Config_loader import Config_loader
from util.logHandler import LogHandler

log = LogHandler("spider")
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36"
}


# 如果金山词霸没找到那么就会使用百度翻译查找网络含义（主要是因为金山词霸对网络翻译的翻译太烂了）
def get_internet_mean(word):
    loader = Config_loader()
    url = "https://fanyi-api.baidu.com/api/trans/vip/translate?"
    appid = str(loader.get_api_appid())
    key = loader.get_api_key()
    salt = "00000"

    hl = hashlib.md5()
    hl.update((appid + word + salt + key).encode(encoding='utf-8'))
    md5_code = hl.hexdigest()
    response = requests.get(url + f"q={word}&from=en&to=zh&appid={appid}&salt={salt}&sign={md5_code}").json()
    try:
        return response["trans_result"][0]["dst"]
    except Exception as e:
        print(e)
        log.error(f"发生错误{e.__str__()}")
        return None


# 使用金山词霸查词
def get_mean(word):
    url = f"https://dict-mobile.iciba.com/interface/index.php?c=word&m=getsuggest&nums=10&is_need_mean=1&word={word}"
    response = requests.get(url, headers=headers).json()
    flag = False
    try:
        flag = True
        return {"mean": response["message"][0]["paraphrase"], "flag": flag}
    except Exception as e:
        log.warning(f"单词”{word}“词霸没查到，转入百度翻译")
        print("词霸没查到，转入百度翻译")
        return {"mean": get_internet_mean(word), "flag": flag}


# 使用金山词霸查词根，词缀
def get_affix(word):
    url = f"https://www.iciba.com/word?w={word}"
    response = requests.get(url, headers=headers).text
    affix_list = parsel.Selector(response).xpath(
        "//div[@class='FoldBox_content__HsTfE']/div[@class='Affix_affix__iiL_9']/p/text()").getall()
    affix = "".join(affix_list)
    if affix == "":
        return None
    return affix


if __name__ == '__main__':
    a = get_mean("github lab")
    print(a)
