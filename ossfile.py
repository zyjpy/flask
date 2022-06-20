# -*- coding: utf-8 -*-
import os
import oss2

# 阿里云账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM用户进行API访问或日常运维，请登录RAM控制台创建RAM用户。
auth = oss2.Auth('LTAI5t6tHyfNhDpxeL3dcXky', 'pr1rlldGHk9ZU0dLlXMrrzVGw2wGVD')
# Endpoint以杭州为例，其它Region请按实际情况填写。
bucket = oss2.Bucket(auth, 'http://oss-cn-hangzhou.aliyuncs.com', 'zhang-movie')

# 设置存储空间为私有读写权限。
# bucket.create_bucket(oss2.models.BUCKET_ACL_PRIVATE)

# 上传文件到OSS。
# <yourObjectName>由包含文件后缀，不包含Bucket名称组成的Object完整路径，例如abc/efg/123.jpg。
# <yourLocalFile>由本地文件路径加文件名包括后缀组成，例如/users/local/myfile.txt。
# bucket.put_object_from_file('image/movie.png', './04.png')
# bucket.get_object_to_file('image/movie.png', './05.png')

from itertools import islice

# oss2.ObjectIterator用于遍历文件。
urlload = "image"
# for filename in oss2.ObjectIterator(bucket, prefix='%s/' % urlload):

#     a = filename.key.replace("image/movie/","")
#     print(a)
# try:

#     bucket.delete_object('image/movie/movie.png')
# except Exception as e:
#     print(e)

result = bucket.get_bucket_location()
print('location: ' + result.location)
bucket_info = bucket.get_bucket_info()
print('name: ' + bucket_info.name)
print('storage class: ' + bucket_info.storage_class)
print('creation date: ' + bucket_info.creation_date)
print('intranet_endpoint: ' + bucket_info.intranet_endpoint)
print('extranet_endpoint ' + bucket_info.extranet_endpoint)
print('owner: ' + bucket_info.owner.id)
print('grant: ' + bucket_info.acl.grant)
print('data_redundancy_type:' + bucket_info.data_redundancy_type) 

# file_url = bucket.sign_url('GET','image',-1)   
# print(file_url)
list_coverlist = []
# for filename in oss2.ObjectIterator(bucket, prefix='%s/' % urlload):

#     # a = filename.key.replace("image","")
#     # print(filename.key)
#     name = "https://zhang-movie.oss-accelerate.aliyuncs.com/"+filename.key
#     # list_coverlist.append(name)
#     source = name.last_modified
# print(list_coverlist[2:])
def get_movielist_from():
    lis = []
    lis2=[]
    bucker_json={}
    for b in islice(oss2.ObjectIterator(bucket), 100):
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
    return lis2



    
