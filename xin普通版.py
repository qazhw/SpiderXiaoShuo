
import os
import sys
import time
# from plyer import notification
from bs4 import BeautifulSoup   #导入匹配解析包
import requests    #导入请求包
from colorama import Fore
from tqdm import tqdm    #设置进度条包
from win10toast import ToastNotifier

class downloader(object):

    def __init__(self):
        self.server = 'https:'
        self.target = 'https://www.qidian.com/search?kw={}'   #设置搜索接口
        self.xsM = ""     # 书名
        self.names = []   # 存放章节名
        self.urls = []    # 存放章节链接
        self.nums = 0     # 章节数



#查找小说
    def search(self):
        bookName = input("请输入小说的名字：")
        souce = requests.get(self.target.format(bookName), timeout=60)   # 发起页面请求
        print(souce)
        html = souce.text   # 获取返回的页面html文本
        div_bf = BeautifulSoup(html, "lxml")     # 用lxml解析器解析html页面
        div = div_bf.find_all('h4')   # 获得 html 信息中所有 h4 标签。

        # 遍历h4文本，如果遍历中有某个小说名等于搜索的小说名字，则将小说名字的链接赋值给target
        for i in div:
            print(str(i.getText()) + str(i.a.get('href')))
            if i.getText() == bookName:
                self.target = self.server + i.a.get('href')+'#Catalog'

    """
        函数说明:获取下载链接
    """
    #下载
    def getchapter(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36 Edg/91.0.864.53',
            'Referer': 'https: // book.qidian.com / info / 1011486666',
            'cookie': '_yep_uuid=fa4fbf56-5726-d5f7-1ddd-086e6c3473a5; e1={"pid":"qd_P_mulu","eid":""}; e2={"pid":"qd_P_xiangqing","eid":""}; _csrfToken=mpdT9O5va7pcvqTq3eEgyWgofC7cYkbbBA0ZJVPn; newstatisticUUID=1623488288_1126464956; e1={"pid":"qd_P_Search","eid":"qd_H_Search","l1":2}; e2={"pid":"qd_P_Search","eid":"","l1":2}',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'

        }
        self.search()   # 调用搜索小说的函数
        print(self.target)
        req = requests.get(url=self.target,headers=headers)    # 发起请求返回响应状态码等
        html = req.text  #获取html文本
        div_bf = BeautifulSoup(html, "lxml")  # 解析html
        div = div_bf.find_all('ul',class_='cf') # 获得 html 信息中所有 class 属性为 volume 的 div 标签。返回类型为列表  |||出问题 动态交互 反爬
        book_name = div_bf.find('h1') # 获取 h1 小说名字
    # 异常 搜索小说 若小说不存在则返回异常输出异常信息 ，反之小说存在则显示搜索成功
        try:
            book_name = book_name.getText()  # 请求url 获取响应文本
            if book_name:
                print('小说已搜索成功')  # 若book_name成功获取文本，则输出搜索成功
                print(book_name)
        except Exception as e:
            print('小说不存在')
            print(e)
            sys.exit()
        finally:
            time.sleep(2)
        book_name = book_name.strip("\n")   # 书名去除首尾换行符
        book_name = book_name.replace("\n", "--") #将标题内的换行符以--代替

        # 如果磁盘中存在book_name（书名）文件夹，则不创建，如果不存在，则创建{书名}文件夹
        if not os.path.exists(book_name):
            os.makedirs(book_name)
        self.xsM = book_name # 将书名赋值给xsM
        print(f'《{book_name}》开始下载：')
        a_bf = BeautifulSoup(str(div), "lxml") # 解析目录html创建Beautiful Soup对象
        a=a_bf.find_all('a')
        print('共'+str(len(a))+'章')  # 输出小说的章节数
        zhang_count= int(input("\n\n请输入要下载的章节数"))
        begin = time.time() #计时起点
        self.nums = len(a[1:zhang_count + 1])  # 统计章节数
        for each in a[0:zhang_count + 1]:
            self.names.append(each.string)
            self.urls.append(self.server + each.get('href'))

        return begin


    """
    函数说明:获取章节内容
    Parameters:
        target - 下载链接(string)
    Returns:
        texts - 章节内容(string)
    """

    def get_contents(self, target):
        req = requests.get(url=target)
        html = req.text
        bf = BeautifulSoup(html, "lxml")
        texts = bf.find_all('div', class_='read-content j_readContent')
        texts = texts[0].text.replace('\u3000' * 2, '\n\n')
        return texts

    """
    函数说明:将爬取的文章内容写入文件
    Parameters:
        name - 章节名称(string)
        path - 当前路径下,小说保存名称(string)
        text - 章节内容(string)
    Returns:
        无
    """

    def writer(self, name, path, text):
        savePath = path + "\\" + str(name) + ".txt"  # 小说名+\\+{mul}.txt
        with open(savePath, 'a', encoding='utf-8') as f:
            f.write(name + '\n')
            f.writelines(text)
            f.write('\n\n')


if __name__ == "__main__":


    dl = downloader()
    begin=dl.getchapter()


    for i in tqdm(range(dl.nums), bar_format='{l_bar}%s{bar}%s{r_bar}' % (Fore.RED, Fore.RESET)): # 进度条

        mul=str(i+1)+'- '+dl.names[i] #保存路径 例：1-***
        dl.writer(mul, dl.xsM, dl.get_contents(dl.urls[i]))

    print(f'《{dl.xsM}》下载完成')
    end = time.time()
    print('下载完毕，总耗时', end - begin, '秒')
    # win10通知栏
    toaster = ToastNotifier()
    toaster.show_toast("爬取完毕",
                       dl.xsM,
                       icon_path="./image.ico",
                       duration=10)
    # notification.notify(
    #     title="爬取完毕",
    #     message=dl.xsM,
    #     app_icon="D:/suiji/image.ico",
    #     timeout=3
    # )