#!/usr/bin/python3
import time
import requests
import os
from bs4 import BeautifulSoup
import random
from selenium import webdriver
import json
# from requests.packages import urllib3
# urllib3.disable_warnings()

headers = [
    {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'},
    {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},
    {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'},
    {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0'},
    {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'}
]

def find_repeat(img_urls):
    for i in range(len(img_urls)):
        a=img_urls[i]
        for j in range(len(img_urls)):
            if a==img_urls[j] and (not i==j):
                print(a)
                input()

class Wie2(object):
    def __init__(self):
        self.url = "https://www.2bfab6a415d78a1c.com"
        self.katong_url = "https://www.2bfab6a415d78a1c.com/tupian/list-%E5%8D%A1%E9%80%9A%E5%8A%A8%E6%BC%AB-{}.html"
        
    
    def driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        chrome = webdriver.Chrome(options=options)
        return chrome

    def get_data(self):
        data = {}
        for i in range(1, 252):
            data[i] ={}
            content = requests.get(self.katong_url.format(i), headers=random.choice(headers))
            content.encoding = 'utf-8'
            soup = BeautifulSoup(content.text, features="html.parser")
            # chrome = self.driver()
            # url = self.katong_url.format(i)
            # chrome.get(url)
            # items = chrome.find_elements_by_css_selector('#main-container > div.text-list-html > div > ul>li>a')[8:]
            items = soup.select('#main-container > div.text-list-html > div > ul>li>a')[8:]
            for j in items:
                html_url = self.url + j.attrs['href']
                # html_url = j.get_attribute('href')
                # title = j.text.split('\n')[-1]
                # chrome.get(html_url)
                # img_urls = chrome.find_elements_by_css_selector('.videopic')

                content = requests.get(html_url, headers=random.choice(headers))
                content.encoding = 'utf-8'
                soup = BeautifulSoup(content.text, features="html.parser")
                img_urls = soup.select('.videopic')
                meta = soup.select('#main-container > div.row.nav-row > div > span >a')
                title = meta[-1].text
                tag = meta[-2].text

                data[i].update(dict(
                    {title: 
                        {'tag': tag, 'urls': [url.attrs['data-original'] for url in img_urls]}
                    }
                ))
                if i%100 == 0:
                    print("processed {}".format(i))
                    with open(os.path.join('temp', 'wie2.json'), 'w') as f:
                        json.dump(data, f)
            # chrome.close()

    def save_img(self, img_url):
        names = img_url.split('/')
        image_name = names[-2]+'_'+names[-1]
        tujigudir = os.path.join('temp', 'tujigu')
        try:
            with requests.get(img_url, stream=True, headers=random.choice(headers)) as r:
                image = r.content
            with open(os.path.join(tujigudir,image_name), 'wb') as pic:
                pic.write(image)
        except:
            print("please save {} again".format(img_url))
            time.sleep(1)

    def save_data(self):
        img_urls = []
        count = 0
        with open(os.path.join('temp', 'wie2.json'), 'r') as f:
            data = json.load(f)
        
        for k, v in data.items():
            img_urls.extend(v['urls'])
        for img_url in img_urls:
            self.save_img(img_url)
            count += 1
            if count%100==0:
                print("saved {}".format(count))

class Tujigu(object):
    def __init__(self):
        self.url = "https://www.tujigu.com/a/{}"
        self.img_url = "https://tjg.hywly.com/a/1/{}/{}.jpg"
    
    def driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        chrome = webdriver.Chrome(options=options)
        return chrome

    def save_img(self, img_url):
        names = img_url.split('/')
        image_name = names[-2]+'_'+names[-1]
        tujigudir = os.path.join('temp', 'tujigu')
        try:
            with requests.get(img_url, stream=True, headers=random.choice(headers)) as r:
                image = r.content
            with open(os.path.join(tujigudir,image_name), 'wb') as pic:
                pic.write(image)
        except:
            print("please save {} again".format(img_url))
            time.sleep(1)

    def get_data(self):
        data = {}
        for i in range(101, 30000):
            chrome = self.driver()
            url = self.url.format(i)
            chrome.get(url)
            meta = chrome.find_elements_by_css_selector("body > div.tuji > p")
            jigou = meta[0].text.split("：")[-1].strip()
            bianhao = meta[1].text.split("：")[-1].strip()
            shuliang = meta[2].text.split("：")[-1][:-1].strip()
            mote = meta[3].text
            tag = chrome.find_elements_by_css_selector("body > div.tags")[0].text
            if meta:
                img_urls = [self.img_url.format(i, j) for j in range(1,int(shuliang)+1)]
                data.update(dict({i:{'tag': tag, 'jigou':jigou, 'bianhao':bianhao, 'shuliang':shuliang, 'mote':mote, 'urls': img_urls}}))
                if i%10 == 0:
                    print("processed {}".format(i))
                    with open(os.path.join('temp', 'tujigu.json'), 'w') as f:
                        json.dump(data, f)
            chrome.close()

    def save_data(self):
        img_urls = []
        count = 0
        with open(os.path.join('temp', 'tujigu.json'), 'r') as f:
            data = json.load(f)
        
        for k, v in data.items():
            img_urls.extend(v['urls'])
        for img_url in img_urls:
            self.save_img(img_url)
            count += 1
            if count%100==0:
                print("saved {}".format(count))
                

class Mztcx(object):
    def __init__(self):
        self.url = "https://mzt.cx/{}/"
        self.tags = {"xinggan":262, "keai": 259, "qingchun": 258, "cosplay": 261, "hanfu": 253}
        self.imgs_url = {}
        self.data = {}
    
    def driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        chrome = webdriver.Chrome(options=options)
        return chrome

    def get_imgs_url(self, url):
        imgs = []
        chrome = self.driver()
        chrome.get(url)
        title = chrome.find_elements_by_css_selector(".post_entry > a:nth-child(1)")
        if not title:
            chrome.quit()
            return 0
        else:
            title = title[0].text
        imgs_eles = chrome.find_elements_by_css_selector(".post_body > p > img")
        for ele in imgs_eles:
            imgs.append(ele.get_attribute('data-original'))
        self.imgs_url[title] = imgs
        chrome.quit()
        return 1

    def save_url(self):
        for k, v in self.tags.items():
            self.data[k] = {}
            start = 1
            # if k == "xinggan" or k =="keai" or k=="qingchun":
            #     continue
            # if k == "cosplay":
            #     with open(os.path.join('temp', 'data.json'), 'r') as f:
            #         self.data = json.load(f)
            #     start = 250
            for i in range(start, v+1):
                url = self.url.format(k) + str(i) + ".html"
                if self.get_imgs_url(url):
                    self.data[k].update(dict({i:self.imgs_url}))
                    self.imgs_url={}
                if i%10 == 0:
                    print("processed {}".format(url))
                    with open(os.path.join('temp', 'data.json'), 'w') as f:
                        json.dump(self.data, f)

    def save_data(self):
        img_urls = []
        count = 0
        with open(os.path.join('temp', 'data.json'), 'r') as f:
            data = json.load(f)
        for tag, content in data.items():
            for k, v in content.items():
                for i, j in v.items():
                    img_urls.extend(j)
        img_urls_set = set(img_urls)
        print("repeat count {}".format(len(img_urls)-len(img_urls_set)))
        img_urls = list(img_urls_set)
        with open(os.path.join('temp', 'img_urls'), 'w') as f:
            f.write(str(img_urls))
        for img_url in img_urls:
            self.save_img(img_url)
            count += 1
            if count%100==0:
                print("saved {}".format(count))

    def save_img(self, img_url):
            image_name = img_url.split('/')[-1]
            mztcxdir = os.path.join('temp', 'mztcx')
            try:
                with requests.get(img_url, stream=True, headers=random.choice(headers)) as r:
                    image = r.content
                with open(os.path.join(mztcxdir,image_name), 'wb') as pic:
                    pic.write(image)
            except:
                print("please save {} again".format(img_url))
                time.sleep(1)


class Douban(object):
    def __init__(self):
        self.book_tag_url = "http://www.douban.com/tag/{}/book"
    
    def clean_epub_by_publisher(self):
        import shutil
        publisher={}
        count = 0
        with open(os.path.join('temp', 'epub_meta.json'), 'r') as f:
            data = json.load(f)

        for fname, desc in data.items():
            count += 1
            try:
                publisher.setdefault(desc['publisher'], 0)
                publisher[desc['publisher']] +=1
                if publisher[desc['publisher']] == ' ':
                    shutil.move(fname, os.path.join('temp', 'fail'))
            except:
                shutil.move(fname, os.path.join('temp', 'fail'))
            
            finally:
                if count % 100 ==0:
                    print("proccessed {}".format(count))
                    with open(os.path.join('temp', 'publisher_meta.json'), 'w') as f:
                        json.dump(publisher, f)


    def get_tagbook(self, tag):
        url = self.book_tag_url.format(tag)
        content = requests.get(url, headers=random.choice(headers))
        soup = BeautifulSoup(content.text)

        list_soup = soup.find('div', {'class': 'mod book-list'})
        for book_info in list_soup.findAll('dd'):
            title = book_info.find('a', {'class': 'title'}).string.strip()
            desc = book_info.find('div', {'class': 'desc'}).string.strip()
            desc_list = desc.split('/')
            author_info = desc_list[0:-3]
            pub_info = desc_list[-3:]
            try:
                rating = book_info.find('span', {'class': 'rating_nums'}).string.strip()
            except:
                rating = '无'
            print("title: {}\nauthor: {}\npublisher: {}\nrating: {}".format(title, author_info, pub_info, rating))


if __name__ == "__main__":
    douban = Douban()
    # douban.get_tagbook('编程')
    mztcx = Mztcx()
    # mztcx.save_url()
    # mztcx.save_data()
    # douban.clean_epub_by_publisher()
    tujigu = Tujigu()
    # tujigu.get_data()
    # tujigu.save_data()
    wie2 = Wie2()
    wie2.get_data()