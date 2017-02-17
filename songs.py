__author__ = 'Administrator'


import requests
import json
import time
import pymysql
from multiprocessing import Pool
import random


headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
}


'''
define a function to get available proxy ip address from source text file. Retuen a list of available ip adresses .
the source text file is created by another script .
'''
def get_available_proxy():
    #all_proxy_list=[]
    available_list=[]
    with open('proxies_text.txt','r') as fr:
        for proxy in fr.readlines():
            available_list.append(proxy.replace('\n',''))
    return available_list

# proxies has a random  value to avoid banned by remote host.
proxies={
    'http':random.choice(get_available_proxy())
}


def get_download_links(url):
    '''
the result of url is json type data,which contains true file path of music file.
the function is defined to get true file path and song's name,singer,and album name
'''

    try:
        page=requests.get(url,headers=headers,proxies=proxies)        #access website with proxy
        page_dict=json.loads(page.text)                               #translate json to dict type
        songName=page_dict['data']['trackList'][0]['songName']
        singer=page_dict['data']['trackList'][0]['singers']
        albumName=page_dict['data']['trackList'][0]['album_name']
        try:
            high_quality_file_path=page_dict['data']['trackList'][0]['allAudios'][2]['filePath']      #some songs hasn't "['allAudios'][2]" 
        except Exception:
            high_quality_file_path=page_dict['data']['trackList'][0]['allAudios'][0]['filePath']      #the true position is "['allAudios'][0]"
        

        #避免插入的sql中有引号导致出错，可以使用pymql.escape_string方法转义。
        sql="insert into songs values('%s','%s','%s','%s')" %(pymysql.escape_string(songName),pymysql.escape_string(singer),pymysql.escape_string(albumName),pymysql.escape_string(high_quality_file_path))
        
        return sql
   
    except Exception:
        
        return 'invalid url:'+url

'''
define a function to insert sql expression to database.
'''
def insert_to_database(url):
    conn=pymysql.connect(host='127.0.0.1',user='root',password='123456',db='xiami_songs',charset='utf8')
    cur=conn.cursor()
    sql=get_download_links(url)

    try:
        cur.execute(sql)
        conn.commit()
        print('insert successfully:'+url)
    except Exception as e:                        #if insert failed , write the invalid url in 'failed_urls.txt'
        with open('failed_urls.txt','a+') as fo:
            fo.write(url+'\n')
        print(e)
    cur.close()
    conn.close()


urls=[]       
for url in range(1,100000):
    urls.append('http://www.xiami.com/song/playlist/id/{0}/object_name/default/object_id/0/cat/json'.format(url))







if __name__=='__main__':      #this expression is indispensable to keep multi_process work finely.

    print(time.ctime())
    p=Pool()
    p.map(insert_to_database,urls)   #in this circumstance, the function 'insert_to_database' is only need one paramenter.

    print(time.ctime())
    
    
    
'''    
 ##################some output:
 
insert successfully:http://www.xiami.com/song/playlist/id/98317/object_name/default/object_id/0/cat/json
insert successfully:http://www.xiami.com/song/playlist/id/98318/object_name/default/object_id/0/cat/json
(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'invalid url:http://www.xiami.com/song/playlist/id/98319/object_name/default/obje' at line 1")

'''
