from itertools import islice
import os
import requests
import oss2
class UPLOAD_FILE():

    def __init__(self,subfilename,key="LTAI5t6tHyfNhDpxeL3dcXky",password="pr1rlldGHk9ZU0dLlXMrrzVGw2wGVD"):
        auth = oss2.Auth(key,password) #初始化
        self.bucket = oss2.Bucket(auth, "http://oss-cn-hangzhou.aliyuncs.com", "zhang-movie")
        self.subfilename = subfilename# oss 路径# oss 路径
        print(self.subfilename)
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
    def get_single_file(self,picNum=100,oss_path="image/example"):
        for filename in oss2.ObjectIterator(self.bucket, prefix='%s/' % oss_path):
            print("https://zhang-movie.oss-accelerate.aliyuncs.com/"+filename.key)
            #返回图片地址
            return "https://zhang-movie.oss-accelerate.aliyuncs.com/"+filename.key
    def get_oss_moviePicList(self,oss_path="image/example"):
        endpoint='http://oss-cn-hangzhou.aliyuncs.com'
        access_key_id='LTAI5t6tHyfNhDpxeL3dcXky'
        access_key_secret='pr1rlldGHk9ZU0dLlXMrrzVGw2wGVD'
        bucket_name='zhang-movie'
        # 指定Bucket实例，所有文件相关的方法都需要通过Bucket实例来调用。
        bucket=oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
        lis = []
        lis2=[]
        bucker_json={}
        for b in oss2.ObjectIterator(bucket, prefix='%s/' % oss_path):
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
        return lis2[0]
# 下载数据，操作oss类
def oss2_data(oss_class,datasurl,name):
    if datasurl:
        try:
            print(datasurl)
            res = requests.get(datasurl, timeout=5,verify=False)
            content_name = name
            content_file = res.content
            osspath = oss_class.upload_file(type='content', content_name=content_name, content_file=content_file)
            return osspath
        except Exception as e:
            print(e)
            return None
#初始化oss:
if __name__ == '__main__':
    upload_class = UPLOAD_FILE(subfilename="image/example")#初始化oss,创建mypic/exam目录
    # upload_class.upload_file(path="E:/flask/static/04.png")
    # upload_class.get_single_file()
    print(upload_class.get_oss_moviePicList())
    # print([1653618445])
    # oss2_data(upload_class,'www.exam.jpg','exam.jpg')#下载www.eaam.jpg ,上次oss