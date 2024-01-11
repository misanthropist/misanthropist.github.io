import os
import glob
import zipfile
from xml.dom.minidom import parseString

def create_mimetype(epub):
    epub.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)

def create_container(epub):
    container_info = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>    
    </rootfiles>
</container>
'''
    epub.writestr('META-INF/container.xml', container_info, compress_type=zipfile.ZIP_STORED)

def create_content(epub, path):
    title = os.path.basename(path)
    creator = os.path.basename(path).split('_')[-1]
    cover = "Images/"+os.path.basename(path)+".jpg"
    imgs = glob.glob(os.path.join(path, "*"))
    base_imgs = (os.path.basename(img) for img in imgs)
    manifest= ''.join('<item id="{}" media-type="image/jpeg" href="Images/{}" />'.format(img, img) for img in base_imgs)
    content_info = '''<?xml version="1.0" encoding="utf-8"?>
<package version="2.0" xmlns="http://www.idpf.org/2007/opf" unique-identifier="uid">
<metadata>
    <dc:title>{}</dc:title>
    <dc:creator>{}</dc:creator>
    <meta name="cover" content="cover-image" />
</metadata>
<manifest>
    <item id="index" media-type="application/xhtml+xml" href="Text/index.xhtml" />
    {}
    <item id="cover-image" href="{}" media-type="image/jpeg" />
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml" />
    <item id="content" href="content.html" media-type="application/xhtml+xml" />
</manifest>
<spine toc="ncx">
    <itemref idref="index" />
</spine>
<guide>
<reference type="text" title="Start Reading" href="Text/index.xhtml" />
</guide>
</package>
'''.format(title, creator, manifest, cover)
    for img in imgs:
        epub.write(img, 'OEBPS/Images/'+os.path.basename(img), compress_type=zipfile.ZIP_DEFLATED)
    cover_path = path+'.jpg'
    cover_name = 'OEBPS/Images/'+os.path.basename(cover_path)
    epub.write(cover_path, cover_name, compress_type=zipfile.ZIP_DEFLATED)

    epub.writestr('OEBPS/content.opf', content_info, compress_type=zipfile.ZIP_STORED)

def create_toc(epub):
    toc_info = '''<?xml version='1.0' encoding='utf-8'?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="zh">
<head>
</head>
<navMap>
    <navPoint id="np_1" playOrder="1">
        <navLabel>
            <text>内容</text>
        </navLabel>
        <content src="Text/index.xhtml" />
    </navPoint>
</navMap>
</ncx>
'''
    epub.writestr('OEBPS/toc.ncx', toc_info, compress_type=zipfile.ZIP_STORED)

def create_pics_archive(pics_path, des_dir):
    path = pics_path
    epub_name = os.path.basename(path)+'.epub'
    epub = zipfile.ZipFile(os.path.join(des_dir, epub_name), 'w')
    create_mimetype(epub)
    create_container(epub)
    create_content(epub, path)
    create_toc(epub)
    imgs = glob.glob(os.path.join(path, "*"))
    base_imgs = (os.path.basename(img) for img in imgs)
    imgs_info = ''.join('<img src="{}" alt="{}" />'.format("../Images/"+img, img) for img in base_imgs)
    index_info = '''<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh">
<head>
</head>
<body>
<h3>{}</h3>
<div>{}</div>
</body>
</html>
'''.format(os.path.basename(path), imgs_info)
    epub.writestr('OEBPS/Text/index.xhtml', index_info, compress_type=zipfile.ZIP_STORED)
    epub.close()

def open_epub_file(epub_path, file_path, func):
    with zipfile.ZipFile(epub_path) as myzip:
        with myzip.open(file_path) as myfile:
            return func(myfile)

def extract_epub_file(epub_path, file_path, des_path):
    with zipfile.ZipFile(epub_path) as myzip:
        myfile = myzip.read(file_path)
        with open(des_path, 'wb') as f:
            f.write(myfile)

def get_xml(file_object):
    try:
        data = file_object.read().decode("utf-8")
    except:
        data = file_object.read().decode("gbk")
    return parseString(data)

def get_opf(epub_path, container_href):
    my_xml = open_epub_file(epub_path, container_href, get_xml)
    opf = my_xml.getElementsByTagName('rootfile')[0].attributes['full-path'].value
    return opf

def get_ncx(epub_path, opf_href):
    my_xml = open_epub_file(epub_path, opf_href, get_xml)
    itemTags = my_xml.getElementsByTagName('item')
    for node in itemTags:
        if node.attributes['id'].value == "ncx" or node.attributes['id'].value == "toc_ncx" or node.attributes['id'].value == "book_ncx":
            ncx = node.attributes['href'].value
            break
    return ncx

def get_metadata(epub_path, opf_href):
    my_xml = open_epub_file(epub_path, opf_href, get_xml)

    title = my_xml.getElementsByTagName("dc:title")[0].childNodes[0].data
    author = "|".join(tag.childNodes[0].data for tag in my_xml.getElementsByTagName("dc:creator"))    
    try:
        date = my_xml.getElementsByTagName("dc:date")[0].childNodes[0].data[:10]
    except:
        date = ":)"

    meta_tags = my_xml.getElementsByTagName('meta')
    for node in meta_tags:
        try:
            if node.attributes['name'].value == "cover":
                cover_id = node.attributes['content'].value
                break
        except:
            continue
    item_tags = my_xml.getElementsByTagName('item')
    for node in item_tags:
        if node.attributes['id'].value == cover_id or node.attributes['id'].value == 'cover.jpg' or node.attributes['id'].value == 'cover':
            cover_href = node.attributes['href'].value
            break

    return [title, author, date, epub_path], cover_href

def get_chapter_list(epub_path, pre_dir, ncx):
    chapter_list = []
    my_xml = open_epub_file(epub_path, pre_dir+ncx, get_xml)
    xmlTag = my_xml.getElementsByTagName('navPoint')
    for node in xmlTag:
        chapter_title = node.getElementsByTagName('text')[0].childNodes[0].nodeValue
        chapter_link = pre_dir+node.getElementsByTagName('content')[0].attributes['src'].value.replace('/', os.sep)
        if ('#' in chapter_link):
            (chapter_file, chapter_anchor) = (chapter_link.split('#'))
        else:
            chapter_file = chapter_link
            chapter_anchor = ''
        chapter_list.append([chapter_title, chapter_file, chapter_anchor])
    return chapter_list

def get_epub_meta(epub_path):
    container_href = "META-INF/container.xml"
    opf = get_opf(epub_path, container_href)
    ncx = get_ncx(epub_path, opf)
    if os.path.dirname(opf):
        opf_dir = os.path.dirname(opf)+'/'
    else:
        opf_dir = ''

    dc, cover_href = get_metadata(epub_path, opf)
    cover_href = opf_dir+cover_href
    chapter_list = get_chapter_list(epub_path, opf_dir, ncx)

    return dc, cover_href, chapter_list
