
import requests


params = {
    "id:O4HVDwAAQBAJ",
    "lpg:PP1",
    "dq:%E5%84%BF%E7%AB%A5%E7%BB%98%E6%9C%AC",
    "hl:zh-CN","pg:PT2",
    "jscmd:click3",
    "vq:%E5%84%BF%E7%AB%A5%E7%BB%98%E6%9C%AC"
    }
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
    "Host":"books.google.co.jp",
    "Accept":"*/*",
    "Accept-Encoding":"gzip, deflate, br",
    "Connection":"keep-alive"
    }
url = "https://books.google.co.jp/books"
proxies={"http":"http://594104281@qq.com:82985272@cdn-cn.nekocloud.cn:19020"}
res = requests.get(url=url,params=params,headers=headers,proxies=proxies)
print(res.text)
