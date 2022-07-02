# -*- coding: utf-8 -*-
# @Author  : 李宇飞
# @Time    : 2022/6/25 19:53
# @File    : 测试2.py
# @Software: PyCharm
import os
from time import sleep
import time
import requests
from bs4 import BeautifulSoup
from threadpool import ThreadPool, makeRequests
from selenium import webdriver

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/103.0.5060.53 Safari/537.36 Edg/103.0.1264.37 '
}
index_len = 0
novel_name = 'Novel'


def get_index(url):
    global index_len, novel_name
    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'lxml')
    href_list = soup.find('div', id='list').find_all('a')
    num_list = range(1, len(href_list) + 1)
    index_len = len(href_list)
    novel_name = soup.find('h1').string
    index_list = []
    for a_tag, index in zip(href_list, num_list):
        index_list.append('{}-*-https://www.xbiquge.la{}'.format(index, a_tag.get('href')))  # 获取该小说每个章节的URL
    print(index_list)
    return index_list


# 进行小说缓存
def get_content(info):
    url = info.split('-*-')[1]
    num = info.split('-*-')[0]
    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html5lib')
    title = soup.find('h1').string
    content = soup.find('div', id='content').get_text().replace('\n\n', '\n').split('亲,点击进去')[0]  # 获取小说内容并去除广告和空行
    with open('./小说/缓存/{}.txt'.format(num), 'w', encoding='utf-8')as f:
        f.write(title + '\n' + content)


# 将缓存的章节合并
def create_text():
    file = open('./小说/{}.txt'.format(novel_name), 'a', encoding='utf-8')
    for num in range(1, index_len + 1):
        path = './小说/缓存/{}.txt'.format(num)
        content = open(path, 'r', encoding='utf-8').read()
        file.write(content + '\n\n\n')
        os.remove(path)
    print('{}下载完成'.format(novel_name))


if __name__ == '__main__':
    # 模拟浏览器去搜索
    the_name = input("请输入你想下载的书名：")
    driver = webdriver.Edge(r'.\edgedriver_win64\msedgedriver.exe')  # Edge浏览器驱动
    driver.get('https://www.xbiquge.la/')  # 笔趣阁网址
    driver.find_element_by_id('wd').send_keys(the_name)  # 按照输入的书名搜索
    driver.find_element_by_id('sss').click()
    driver.find_element_by_partial_link_text(the_name).click()
    driver.switch_to.window(driver.window_handles[-1])  # 切换到最后一个页面
    url = driver.current_url  # 获取最佳匹配电子书的url
    driver.quit()
    print("你想要下载的书为:{0}，最佳匹配电子书的url为:{1}".format(the_name, url))
    sleep(1)
    print("开始下载")
    startTime = time.time()  # 开始计算下载时间
    info_list = get_index(url)
    pool = ThreadPool(18)
    request = makeRequests(get_content, info_list)
    [pool.putRequest(req) for req in request]
    pool.wait()
    create_text()
    endTime = time.time()
    dtime = endTime - startTime
    print("电子书下载用时：%s s" % dtime)
