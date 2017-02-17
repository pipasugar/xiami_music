from bs4 import BeautifulSoup
import requests
import re
import time

headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
}


#the source information of proxies is fetched by access ''http://www.coobobo.com/free-http-proxy'.  
def get_proxies():
    ips=[]
    ports=[]
    for page in range(1,11):
        source=requests.get('http://www.coobobo.com/free-http-proxy/{0}'.format(page),headers=headers,)
        #source.encoding='gbk'
        soup=BeautifulSoup(source.text,'lxml')
        infos=soup.select('''body > div > div > div > table > tbody > tr''')
        #print(infos)

        for info in infos:
            #print(type(info))
            info=str(info)
            if '匿名' in info:
        #         #print('go')
                ip=re.findall(r'''<td>(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})</td>?''',info)[0]
                ips.append(ip)
                port=re.findall(r'''<td>(\d{2,5})</td>?''',info)[0]
                ports.append(port)
    
    ip_list=list(zip(ips,ports))
    #print(ip_list)
    proxies=[]
    for ip in ip_list:
        proxies.append('http://'+ip[0]+':'+ip[1])

    return proxies


'''
verify available proxies by access 'www.baidu.com'.
'''
def get_available_proxies():
    available_proxies=[]
    for proxy in get_proxies():
        try:
            page=requests.get('http://www.baidu.com',headers=headers,proxies={'http':proxy},timeout=0.5)
            #print(page.text)
            available_proxies.append(proxy)
            print(proxy+' is available')
        except Exception:
            print(proxy+' is not available')
            #continue
    # print(available_proxies)
    # print(len(available_proxies))
    return available_proxies


'''
write these available proxies in 'proxies_text.txt' 
'''
def proxies_text():
    proxies=get_available_proxies()
    with open('proxies_text.txt','w') as fo:
        fo.truncate()
        for text in proxies:
            fo.write(text+'\n')

'''
run function with 30 seconds frequency.
'''
k=1
while 1:
    proxies_text()
    print(str(k)+' times')
    k+=1
    time.sleep(30)
    

'''
some output below:

http://170.248.47.58:80 is not available
210 times
http://81.23.0.41:3129 is not available
http://37.187.100.23:3128 is not available
http://104.236.246.155:8080 is not available
http://191.96.4.25:8080 is not available

'''

