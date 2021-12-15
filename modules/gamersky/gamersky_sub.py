import json
import os
import random

import requests
from bs4 import BeautifulSoup as BS

TARGET_SUFFIX = ['动态图', '囧图']
ROOT_SAVE_PATH = "data/gamersky_sub/"
TYPE_GIF = 0
TYPE_DEFAULT = 1
TYPE_RANDOM = 2

base_url = "https://db2.gamersky.com/LabelJsonpAjax.aspx?jsondata={}"
params = """{"type":"updatenodelabel","isCache":true,"cacheTime":60,"nodeId":"20113","isNodeId":"true","page":1}"""
itemInfo = []
default_file_name = 1


def download(downloadUrl, savePath, fileName):
    global default_file_name
    if not os.path.exists(savePath):
        os.makedirs(savePath)
    if fileName.find("\n") > 0:
        fileName = fileName.split("\n")[-1]
    if len(fileName) <= 0:
        fileName = str(default_file_name)
        default_file_name += 1
    fileName += downloadUrl[-4::]
    path = "{}/{}".format(savePath, fileName)
    if os.path.exists(path):
        print("{} already exists".format(fileName))
        return
    response = requests.get(downloadUrl)
    if response.ok:
        try:
            with open(path, 'wb') as f:
                f.write(response.content)
                print("download success,saved in {}".format(path))
        except OSError:
            print("download failed,url:{} path:{}".format(downloadUrl, path))
    else:
        print("download failed,url:{}".format(downloadUrl))


def fetchPicDetail(detailUrl, isFirstLoad):
    response = requests.get(detailUrl)
    response.encoding = 'utf-8'
    bs = BS(response.text, "lxml")
    # print(bs.prettify())
    title = str(bs.title.text)
    if title.find("_") > -1:
        dirName = title.split("_")[0].strip()
    elif title.find(" ") > -1:
        dirName = title.split(" ")[1].strip()
    else:
        dirName = title[-7::].strip()
    savePath = ROOT_SAVE_PATH + dirName
    if isFirstLoad and (os.path.exists(savePath) or os.path.exists(f'{ROOT_SAVE_PATH}_{dirName}')):
        print(f"{detailUrl} has already downloaded in path:{savePath}.")
        return False
    for block in bs.find("div", class_='Mid2L_con').findAll("p"):
        # print(block)
        if block.a is None:
            continue
        pic_url = str(block.a['href'])
        if len(pic_url) <= 0 or pic_url.endswith("html"):
            continue
        pic_url = pic_url[pic_url.find("?") + 1:]
        download(pic_url, savePath, str(block.text).strip())
    nextPageNode = bs.find("a", text='下一页')
    if nextPageNode is not None:
        fetchPicDetail(nextPageNode['href'], False)
    return True


def fetchGifDetail(url, isFirstLoad):
    print("start fetch:" + url)
    response = requests.get(url)
    response.encoding = 'utf-8'
    bs = BS(response.text, "lxml")
    # print(bs.prettify())
    title = str(bs.title.text)
    if title.find("_") > -1:
        dirName = title.split("_")[0].strip()
    elif title.find(" ") > -1:
        dirName = title.split(" ")[1].strip()
    else:
        dirName = title[-7::].strip()
    savePath = ROOT_SAVE_PATH + dirName
    if isFirstLoad and (os.path.exists(savePath) or os.path.exists(f'{ROOT_SAVE_PATH}_{dirName}')):
        print(f"{url} has already downloaded in path:{savePath}.")
        return False
    for block in bs.find("div", class_='Mid2L_con').findAll("p", class_="GsImageLabel"):
        # print(block)
        if block.img is None:
            continue
        pic_url = str(block.img['src'])
        if len(pic_url) <= 0 or pic_url.endswith("html"):
            continue
        # pic_url = pic_url[pic_url.find("?") + 1:]
        download(pic_url, savePath, str(block.text).strip())
    nextPageNode = bs.find("a", text='下一页')
    if nextPageNode is not None:
        print("===========================================")
        print("start fetch next page")
        fetchGifDetail(nextPageNode['href'], False)
    return True


def fetchPage(page):
    response = requests.get(base_url.format(params))
    # print(response.text)
    loads = json.loads(response.text[1:-2])
    # print(loads)
    bs = BS(loads['body'], "lxml")
    # print(bs.prettify())
    count = 0
    for block in bs.findAll("div", class_="img"):
        # print(block)
        for s in TARGET_SUFFIX:
            title = block.a.img['alt']
            if str(title).endswith(s):
                # itemInfo.append({"link": block.a['href'], "title": title})
                if s == TARGET_SUFFIX[0]:
                    if fetchGifDetail(block.a['href'], True):
                        count += 1
                else:
                    if fetchPicDetail(block.a['href'], True):
                        count += 1
    return count


# fetchPage(1)
# print(itemInfo)

def getRandomPic(dirPath):
    pics = os.listdir(ROOT_SAVE_PATH + dirPath)
    pics = [d for d in pics if not d.startswith('_')]
    pics_size = len(pics)
    if pics_size <= 0:
        return None
    target_file = pics[random.randint(0, pics_size - 1)]
    source = f'{ROOT_SAVE_PATH + dirPath}/{target_file}'
    ret = f'{ROOT_SAVE_PATH + dirPath}/_{target_file}'
    # print(f'curPath:{os.getcwd()}')
    os.rename(source, ret)
    return ret


def getPicByType(type):
    if not os.path.exists(ROOT_SAVE_PATH):
        return None
    article_dir = os.listdir(ROOT_SAVE_PATH)
    # 已发送过的文件夹
    article_dir = [d for d in article_dir if not d.startswith('_')]
    # 根据类型过滤文件夹
    if type != TYPE_RANDOM:
        targetList = [d for d in article_dir if d.endswith(TARGET_SUFFIX[type])]
    else:
        targetList = article_dir
    list_size = len(targetList)
    if list_size <= 0:
        return None
    target_dir = targetList[random.randint(0, list_size - 1)]
    ret = getRandomPic(target_dir)
    if ret is None:
        os.rename(ROOT_SAVE_PATH + target_dir, f'{ROOT_SAVE_PATH}_{target_dir}')
    return ret


# print(getPicByType(TYPE_GIF))
# with open("../test.txt", 'wb') as f:
#     f.write(bytes("test", encoding='utf-8'))
# print(os.rename("../test.txt", "test1.txt"))

#fetchGifDetail('https://www.gamersky.com/ent/202112/1443782.shtml', True)
# print(getPicByType(0))
