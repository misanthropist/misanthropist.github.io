import json
import os
import shutil
import time
from xml.dom.minidom import parseString, Document
import zipfile

temp_dir = 'temp'

def unzip(src, des):
    zip_file = zipfile.ZipFile(src)
    for file in zip_file.filelist:
        if file.filename == des:
            zip_file.extract(des, temp_dir)
    zip_file.close()

def get_xml(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = f.read()
    except:
        with open(filename, "r", encoding="gbk") as f:
            data = f.read()
    return parseString(data)

def get_toc(opf_dom):
    xmlTag = opf_dom.getElementsByTagName('item')
    for node in xmlTag:
        if (node.attributes['id'].value == "ncx"):
            toc_file = node.attributes['href'].value
            break
    return toc_file

def get_chapter_list(toc_file):
    chapter_list = []
    dom = get_xml(toc_file)
    xmlTag = dom.getElementsByTagName('navPoint')
    for node in xmlTag:
        chapter_title = node.getElementsByTagName('text')[0].childNodes[0].nodeValue
        chapter_link = node.getElementsByTagName('content')[0].attributes['src'].value.replace('/', os.sep)
        if ('#' in chapter_link):
            (chapter_file, chapter_anchor) = (chapter_link.split('#'))
        else:
            chapter_file = chapter_link
            chapter_anchor = ''
        chapter_list.append([chapter_title, chapter_file, chapter_anchor])
    return chapter_list

def epub_meta(epub):
    try:
        with open(os.path.join('temp', 'epub_meta.json'), 'r') as f:
            data = json.load(f)
    except:
        data={}

    data[epub] = {}
    container_file = "META-INF/container.xml"
    unzip(epub, container_file)
    dom = get_xml(os.path.join(temp_dir, "META-INF", "container.xml"))
    xmlTag = dom.getElementsByTagName('rootfile')[0]
    opf = xmlTag.attributes['full-path']

    unzip(epub, opf.value)
    dom = get_xml(os.path.join(temp_dir, opf.value.replace('/', os.sep)))
    
    xmlTag = dom.getElementsByTagName('metadata')[0]
    nodes = xmlTag.childNodes
    for node in nodes.copy():
        if not node.nodeType == 1:
            nodes.remove(node)
    for n in nodes.copy():
        if n.tagName.find("dc:") == -1:
            nodes.remove(n)
    for node in nodes:
        tag=node.tagName.split(":")[-1]
        if not node.childNodes == []:
            value = node.childNodes[0].data
        data[epub].update({tag: value})

    # toc_file = opf.value.split('/')[0] + '/' + get_toc(dom)
    # unzip(epub, toc_file)
    # chapter_list = get_chapter_list(os.path.join(temp_dir, toc_file.replace('/', os.sep)))
    # data[epub].update({"chapter_list": chapter_list})

    with open(os.path.join(temp_dir, 'epub_meta.json'), 'w') as f:
        json.dump(data, f)

if __name__ == "__main__":
    # count = 0
    # try:
    #     with open(os.path.join('temp', 'epub_list.json'), 'r') as f:
    #         epub_list = json.load(f)
    # except:
    #     epub_list = os.listdir(os.path.join(temp_dir, 'books'))

    # for epub in epub_list.copy():
    #     try:
    #         epub_meta(os.path.join("temp", "books", epub))
    #         if count % 100 == 0:
    #             print("processed {}".format(epub))
    #         count += 1
    #     except:
    #         print("can't processed {}".format(epub))
    #         shutil.move(os.path.join(temp_dir, 'books', epub), os.path.join('temp', 'fail'))
    #         print("moved to fail")

    #     finally:
    #         epub_list.remove(epub)
    #         with open(os.path.join('temp', 'epub_list.json'), 'w') as f:
    #             json.dump(epub_list, f)