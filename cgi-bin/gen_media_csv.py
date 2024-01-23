import csv
from pathlib import Path
import hashlib
import os

from PIL import Image

from epub import get_epub_meta, extract_epub_file

def crop_center(src, des, box):
    img = Image.open(src)
    myw, myh = box
    w,h = img.size
    a = w/myw
    b = h/myh
    ratio = 1
    if a > 1 and b > 1:
        if a > b:
            ratio = b
            true_w = int(w/ratio)
            temp_img = img.resize((true_w, myh))
            left = int((true_w - myw)/2)
            temp_img = temp_img.crop([left, 0, left+myw, myh])
        else:
            ratio = a
            true_h = int(h/ratio)
            temp_img = img.resize((myw, true_h))
            top = int((true_h - myh)/2)
            temp_img = temp_img.crop([0, top, myw, top+myh])
        temp_img.save(des)
    else:
        print("pic is too small.")
        return False

def dump_csv(data, path, mode="w"):
    with open(path, mode, encoding='utf-8', newline="") as csvfile:
        csvwt = csv.writer(csvfile)
        csvwt.writerows(data)

def read_csv(path):
    data = []
    with open(path, 'r', encoding='utf-8', newline='') as f:
        csvrd = csv.reader(f)
        for row in csvrd:
            data.append(row)
    return data

def str2md5(str):
    md = hashlib.md5()
    md.update(str.encode("utf-8"))
    str_id = md.hexdigest()
    return str_id

def dicts2csv(dicts):
    list_csv = []
    head = [h for h in dicts[0]]
    list_csv.append(head)
    for d in dicts:
        data = []
        for k in d:
            data.append(d[k])
        list_csv.append(data)
    return list_csv

def parse_cedict(dict_path):
    list_of_dicts = []
    with open(dict_path) as file:
        text = file.read()
        lines = text.split('\n')
        dict_lines = list(lines)
    for line in dict_lines:
        parsed = {}
        if line == '':
            continue
        line = line.rstrip('/')
        line = line.split('/')
        if len(line) <= 1:
            continue
        english = line[1]
        char_and_pinyin = line[0].split('[')
        characters = char_and_pinyin[0]
        characters = characters.split()
        traditional = characters[0]
        simplified = characters[1]
        pinyin = char_and_pinyin[1]
        pinyin = pinyin.rstrip()
        pinyin = pinyin.rstrip("]")
        parsed['traditional'] = traditional
        parsed['simplified'] = simplified
        parsed['pinyin'] = pinyin
        parsed['english'] = english
        list_of_dicts.append(parsed)

    return list_of_dicts

def parse_ecdict(dict_path):
    pass

def unwrap_dir(path):
    for dpath in Path(path).iterdir():
        dname = dpath.name
        for fpath in dpath.iterdir():
            fpath.rename(fpath.parent.parent / (dname+'-'+fpath.stem+fpath.suffix))

def gen_site_meta(site):
    src_site = Path('/home/doudou/temp/a/tmp/') / site
    src_csv_path = src_site / (site+'.csv')
    des_site = Path('/home/doudou/temp/a/') / site
    des_csv_path = des_site / (site+'.csv')
    if des_csv_path.exists():
        data = read_csv(des_csv_path)
    else:
        data = []
    return src_site, src_csv_path, des_site, des_csv_path, data

def add_m3u8(site):
    src_site, src_csv_path, des_site, des_csv_path, data = gen_site_meta(site)
    
    for dpath in src_site.iterdir():
        if dpath.is_dir():
            old_name = dpath.name
            new_name = str2md5(old_name)
            if [new_name, old_name] in data:
                print("{} is existed".format(old_name))
                continue

            cover_path = dpath / 'cover.jpg'
            if not cover_path.exists():
                for f in dpath.iterdir():
                    if f.suffix == ".ts":
                        command = 'ffmpeg -ss {} -i "{}" -frames:v 1 "{}"'.format(3, f, cover_path)
                        os.system(command)
                        with open(dpath / 'info.html', 'w', encoding='utf-8') as f:
                            content = '<h2>{}</h2>'.format(old_name)
                            f.write(content)
                        dpath.rename(des_site / new_name)
                        data.append([new_name, old_name])
                        break

    dump_csv(data, src_csv_path)
    dump_csv(data, des_csv_path)

def add_mp4(site):
    src_site, src_csv_path, des_site, des_csv_path, data = gen_site_meta(site)

    for fpath in src_site.glob("*.mp4"):
        old_name = fpath.stem
        new_name = str2md5(old_name)
        if [new_name, old_name] in data:
            print("{} is existed".format(old_name))
            continue

        cover_path = src_site / (new_name+".jpg")
        command = 'ffmpeg -ss {} -i "{}" -frames:v 1 "{}"'.format(3, fpath, cover_path)
        os.system(command)
        info_path = src_site / (new_name+".html")
        with open(info_path, 'w', encoding='utf-8') as f:
            content = '<h2>{}</h2>'.format(old_name)
            f.write(content)
        if not cover_path.exists():
            print("{}'s cover is not existed".format(old_name))
            continue
        else:
            fpath.rename(des_site / (new_name+".mp4"))
            cover_path.rename(des_site / cover_path.name)
            info_path.rename(des_site / info_path.name)
            data.append([new_name, old_name])

    dump_csv(data, src_csv_path)
    dump_csv(data, des_csv_path)

def add_mp3(site):
    src_site, src_csv_path, des_site, des_csv_path, data = gen_site_meta(site)

    for fpath in src_site.glob("*.mp3"):
        old_name = fpath.stem
        new_name = str2md5(old_name)
        if [new_name, old_name] in data:
            print("{} is existed".format(old_name))
            continue

        cover_path = src_site / (new_name+".jpg")
        command = 'ffmpeg -i "{}" "{}"'.format(fpath, cover_path)
        os.system(command)
        if not cover_path.exists():
            print("{}'s cover is not existed".format(old_name))
            continue
        else:
            fpath.rename(des_site / (new_name+".mp3"))
            cover_path.rename(des_site / cover_path.name)
            data.append([new_name, old_name])

    dump_csv(data, src_csv_path)
    dump_csv(data, des_csv_path)


def add_epub(site):
    src_site, src_csv_path, des_site, des_csv_path, data = gen_site_meta(site)

    for fpath in src_site.glob("*.epub"):
        epub_name = fpath.stem
        dc, cover_url, chapter_list = get_epub_meta(fpath)
        cover_path = src_site / (epub_name+".jpg")
        extract_epub_file(fpath, cover_url, cover_path)
        if not cover_path.exists():
            print("{}'s cover is not existed".format(epub_name))
            continue
        else:
            fpath.rename(des_site / fpath.name)
            cover_path.rename(des_site / cover_path.name)
            data.append(['.', epub_name])

    dump_csv(data, src_csv_path)
    dump_csv(data, des_csv_path)

def add_pdf(site):
    src_site, src_csv_path, des_site, des_csv_path, data = gen_site_meta(site)

    for fpath in src_site.glob("*.pdf"):
        old_name = fpath.stem
        new_name = str2md5(old_name)
        if [new_name, old_name] in data:
            print("{} is existed".format(old_name))
            continue
        fpath.rename(des_site / (new_name+".pdf"))
        data.append([new_name, old_name])

    dump_csv(data, src_csv_path)
    dump_csv(data, des_csv_path)
    

def add_jpg(site):
    src_site, src_csv_path, des_site, des_csv_path, data = gen_site_meta(site)

    for dpath in src_site.iterdir():
        if dpath.is_dir():
            old_name = dpath.name
            new_name = str2md5(dpath.name)
            num = 0
            for fpath in dpath.iterdir():
                if fpath.suffix == ".jpg":
                    num = num + 1
                    fpath.rename(fpath.parent / (new_name+'_'+str(num)+".jpg"))
            for fpath in dpath.iterdir():
                if fpath.suffix == ".jpg":
                    cover_path = fpath.parent / (new_name+".jpg")
                    if not crop_center(fpath, cover_path, (340,500)):
                        break
            info_path = dpath / (new_name+".html")
            with open(info_path, 'w', encoding='utf-8') as f:
                content = '<h2>{}</h2>'.format(old_name)
                f.write(content)
            dpath.rename(des_site / new_name)
            data.append([new_name, old_name, str(num)])
    dump_csv(data, src_csv_path)
    dump_csv(data, des_csv_path)

def add_csv(site):
    src_site, src_csv_path, des_site, des_csv_path, data = gen_site_meta(site)

    if site == "cedict":
        ce_path = src_site / "cedict_ts.u8"
        list_of_dicts = parse_cedict(ce_path)
        data = dicts2csv(list_of_dicts)

    if site == "today":
        import json
        today = Path("/home/doudou/temp/a/tmp/today/").glob("*.json")
        for t in today:
            name = t.stem
            result = []
            with open(t, 'r', encoding="utf-8") as f:
                content = json.load(f)
                for k in content:
                    result.extend(content[k])
                result = [len(result), name] + result
                data.append(result)
    
    if site == "ecdict":
        path = src_site / "ecdict.csv"
        data = []
        with open(path, 'r', encoding='utf-8', newline='') as f:
            csvrd = csv.reader(f)
            for row in csvrd:
                if row[0] and row[1] and row[2] and row [3]:
                    data.append([row[3], row[0], row[1], row[2]])

    dump_csv(data, src_csv_path)
    dump_csv(data, des_csv_path)
    
if __name__ == "__main__":
    add_mp4('av')
    


