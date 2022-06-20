import json

import requests


def movie_info():

    url = 'https://movie.douban.com/j/chart/top_list' # 数据目标地址
    params = { # 需要携带的动态参数
        'type': '2',
        'interval_id': '100:90',
        'action':'' ,
        'start': '0',
        'limit':'100'
        }
    '''
    模拟浏览器的身份验证信息，防止反爬
    '''
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4750.0 Safari/537.36'}
    response = requests.get(url=url, params=params, headers=headers,proxies={"http":"http://594104281@qq.com:82985272@cdn-cn.nekocloud.cn:19020"})
    data = response.text #str格式

    # data = json.dump(response.text)
    # data = json.dumps(response.text) #str
    data =  json.loads(response.text) #list格式
    # print(data)
    cover_urls = []
    titles = []
    release_dates = []
    scores = []
    actorss = []
    print(type(data[0]["cover_url"]))
    # print(type(data[0]["title"]))
    # print(type(data[0]["release_date"]))
    # print(type(data[0]["score"]))
    # print(type(data[0]["actors"]))
    n = len(data)
    for i in range(n):
        cover_urls.append(data[i]["cover_url"])
        # titles.append(data[i]["title"])
        # release_dates.append(data[i]["release_date"])
        # scores.append(data[i]["score"])
        # actorss.append(data[i]["actors"])
    return cover_urls


print(movie_info())
