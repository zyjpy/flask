# -*- coding: utf-8 -*-
"""
 @Time   : 2020/10/29 9:54 
 @Athor   : LinXiao
 @功能   :
"""
# ------------------------------
import datetime
import io
import json
import os
import random
import string
import time
import uuid

import requests
import oss2
from itertools import islice
# 储存的路径
# filePath="/house/2020-10-29/xxxx.jpg"  # xxxxx  wei
# # 指定Bucket实例，所有文件相关的方法都需要通过Bucket实例来调用。
# bucket=oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
class OssfileUrl():
    def __init__(
        self,endpoint="http://oss-cn-hangzhou.aliyuncs.com",
        access_key_id='LTAI5t6tHyfNhDpxeL3dcXky',
        access_key_secret='pr1rlldGHk9ZU0dLlXMrrzVGw2wGVD',
        bucket_name='zhang-movie'):
        self.endpoint=endpoint
        self.access_key_id=access_key_id
        self.access_key_secret=access_key_secret
        self.bucket_name=bucket_name        
        self.bucket=oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
    def parser(self,img, imageName, dirpath):

        endpoint='http://oss-cn-hangzhou.aliyuncs.com'
        access_key_id='LTAI5t6tHyfNhDpxeL3dcXky'
        access_key_secret='pr1rlldGHk9ZU0dLlXMrrzVGw2wGVD'
        bucket_name='zhang-movie'
        # 指定Bucket实例，所有文件相关的方法都需要通过Bucket实例来调用。
        bucket=oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
        time.sleep(0.2)
        result=bucket.put_object(f'{dirpath}/{imageName}', img.getvalue())
        print('图片上传oss success!')
        return result.status



    def main(self,url): #url 为爬虫的图片的地址
        # 测试的阿里云oss储存路径,正式的为house
        
        dirpath='image' #bucket_name
        domain='http://zhang-movie.oss-cn-hangzhou.aliyuncs.com/' 

        now=datetime.datetime.now()
        nonce=str(uuid.uuid4())

        random_name=now.strftime("%Y-%m-%d") + "/" + nonce

        imageName='{}.jpg'.format(random_name)
        
        img=io.BytesIO(requests.get(url, timeout=300).content)

        statusCode= OssfileUrl.parser(img, imageName, dirpath)

        if statusCode == 200:
            new_oss_url=domain + dirpath + '/' + imageName
            print(new_oss_url)
            # print(type(new_oss_url))   # <class 'str'>
            return new_oss_url

    import json

    import requests




    def movie_info(self):

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


    def upload_all_pic(self):
        data = OssfileUrl.movie_info()
        n = len(data)
        print(n)
        for i in range(n):
            time.sleep(0.5)
            OssfileUrl.main(data[i])

    def get_oss_moviePicList(self,picNum):
        endpoint='http://oss-cn-hangzhou.aliyuncs.com'
        access_key_id='LTAI5t6tHyfNhDpxeL3dcXky'
        access_key_secret='pr1rlldGHk9ZU0dLlXMrrzVGw2wGVD'
        bucket_name='zhang-movie'
        # 指定Bucket实例，所有文件相关的方法都需要通过Bucket实例来调用。
        bucket=oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
        lis = []
        img_lis=[]
        bucker_json={}
        for b in islice(oss2.ObjectIterator(bucket), picNum):
            # print(b.key)
            # print(b.last_modified)
            lis.append(b.last_modified)
            # img_lis = sorted(lis)
            bucker_json[b.last_modified]=b.key
            # print(b.last_modified)
            name = "https://zhang-movie.oss-accelerate.aliyuncs.com/"+bucker_json[b.last_modified]
            bucker_json[b.last_modified]=name
        # print(bucker_json)
        n = len(lis)
        lis = sorted(lis)
        for i in range(n):
            img_lis.append(bucker_json[lis[i]])
        img_lis=img_lis[1:]
        print(img_lis)
        return img_lis
    def get_oss_htmlfile(self,oss_path="dianjing/html_file"):
        lis = []
        htmlfile_list=[]
        bucker_json={}
        for b in oss2.ObjectIterator(self.bucket, prefix='%s/' % oss_path):
            lis.append(b.last_modified)
            bucker_json[b.last_modified]=b.key
            name = "https://zhang-movie.oss-accelerate.aliyuncs.com/"+bucker_json[b.last_modified]
            bucker_json[b.last_modified]=name
        n = len(lis)
        lis = sorted(lis)
        for i in range(n):
            htmlfile_list.append(bucker_json[lis[i]])
        return htmlfile_list

    # def get_single_file(self,folder_name):
    #     for filename in oss2.ObjectIterator(self.bucket, prefix='%s/' % folder_name):#folder_name"image/example"
    #         print("https://zhang-movie.oss-accelerate.aliyuncs.com/"+filename.key)
    #         #返回图片地址
    #         return "https://zhang-movie.oss-accelerate.aliyuncs.com/"+filename.key
    def get_oss_lastest_file(self,oss_path="image/example"):
        endpoint='http://oss-cn-hangzhou.aliyuncs.com'
        access_key_id='LTAI5t6tHyfNhDpxeL3dcXky'
        access_key_secret='pr1rlldGHk9ZU0dLlXMrrzVGw2wGVD'
        bucket_name='zhang-movie'
        # 指定Bucket实例，所有文件相关的方法都需要通过Bucket实例来调用。
        # bucket=oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
        lis = []
        lis2=[]
        bucker_json={}
        for b in oss2.ObjectIterator(self.bucket, prefix='%s/' % oss_path):
            # print(b.key)
            # print(b.last_modified)
            lis.append(b.last_modified)
            # lis2 = sorted(lis)
            bucker_json[b.last_modified]=b.key
            # print(b.last_modified)
            name = "https://zhang-movie.oss-accelerate.aliyuncs.com/"+bucker_json[b.last_modified]
            bucker_json[b.last_modified]=name
        # print(bucker_json)
        n = len(lis)
        lis = sorted(lis)
        for i in range(n):
            lis2.append(bucker_json[lis[i]])
        
        # print(lis2)
        return lis2[-1]

    def upload_local_file(self,osspath,local_file):
        # 先检测oss上是否有该文件
        exist = self.bucket.object_exists(osspath)
        if exist:
            print("oss have files with the same name, ignore oss upload")
        else:
            # 上传文件
            with open(local_file, "rb") as fileobj:
                result1 = self.bucket.put_object(osspath, fileobj)
                print("{} 上传成功".format(osspath))
            if int(result1.status) != 200:
                print("oss upload faild %s" % osspath)
    def upload_file(self,path_list=None,path=None,type='content',content_file=None,content_name=None):
        if path_list:
            list_file = os.listdir(path_list)
            for file in list_file:
                local_file = path_list + "\\" + "{}".format(file)
                osspath = self.subfilename + '/' + file
                print(osspath)
                self.up_file(osspath, local_file)
        elif path:
            osspath = self.subfilename + '/' +path.split('/')[-1]
            local_file = path
            self.up_file(osspath,local_file)
            return osspath
        elif type=='content':
            osspath = self.subfilename + '/' + content_name
            exist = self.bucket.object_exists(osspath)
            if exist:
                print("oss have files with the same name, ignore oss upload")
                return osspath
            else:
                self.bucket.put_object(osspath, content_file)
                print(" {} 上传成功".format(osspath))
                return osspath
        else:
            print("未指定路径")

    def up_file(self,osspath,local_file):
        # 先检测oss上是否有该文件
        exist = self.bucket.object_exists(osspath)
        if exist:
            print("oss have files with the same name, ignore oss upload")
        else:
            # 上传文件
            with open(local_file, "rb") as fileobj:
                result1 = self.bucket.put_object(osspath, fileobj)
                print("{} 上传成功".format(osspath))
            if int(result1.status) != 200:
                print("oss upload faild %s" % osspath)

if __name__ == '__main__':
    # url='https://img.alicdn.com/bao/uploaded/i3/TB1LMGLiP39YK4jSZPctrBrUFXa_460x460.jpg'

    # upload_all_pic()
    oss=OssfileUrl()
    #按图片的最后修改时间获取图片
    # oss.main("E:/FLASK/static/04.png")
    # oss.get_oss_moviePicList()
    # oss.get_single_file("image/example")
    print(oss.get_oss_lastest_file())