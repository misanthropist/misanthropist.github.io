import glob
import csv
import re
from pathlib import Path
import hashlib
import os
import subprocess

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

def get_format_info(filename):
    command = '''ffmpeg -i "{}" -hide_banner'''.format(filename)
    ffmpeger = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    info = str(ffmpeger.stderr.read())
    video_info = re.match(r'.*?Video: (.*?) ', info.replace('\n', '')).groups()
    audio_info = re.match(r'.*?Audio: (.*?) ', info.replace('\n', '')).groups()
    return (video_info[0], audio_info[0])


def clean_m3u8(site):
    site = Path('/mnt/z/') / site
    for dpath in site.iterdir():
        # new_name = str2md5(dpath.name)
        if not (dpath / 'cover.jpg').exists():
            ts_name = list(glob.glob(os.path.join(dpath, "*.ts")))[0]
            new_name = ts_name.replace('0.ts', '').replace(str(dpath)+'/', '')
            cover_path = dpath / ('hls.jpg')
            m3u8_path = dpath / (dpath.name+'.m3u8')
            try: 
                cover_path.rename(dpath / 'cover.jpg')
            except:
                coverpath = str(dpath)+'/hls.jpg'
                command = 'ffmpeg -ss {} -i "{}" -frames:v 1 "{}"'.format(0, ts_name, coverpath)
                os.system(command)
                cover_path.rename(dpath / 'cover.jpg')
            m3u8_path.rename(dpath / 'hls.m3u8')
            with open(dpath / 'info.html', 'w', encoding='utf-8') as f:
                content = '<h2>{}</h2>'.format(new_name)
                f.write(content)
            # dpath.rename(site / new_name)

def add_av():
    site_path = Path('/mnt/z/av')
    site_path_temp = Path('/mnt/z/tmp/av')
    data = read_csv(site_path / 'av.csv')
    for path in site_path_temp.iterdir():
        if path.suffix == ".mp4":
            new_id = str2md5(path.stem)
            data.append([new_id, path.stem])

            coverpath = str(site_path)+'/'+new_id+'.jpg'
            command = 'ffmpeg -ss {} -i "{}" -frames:v 1 "{}"'.format(0, str(path), coverpath)
            os.system(command)

            htmlpath = str(site_path)+'/'+new_id+'.html'
            with open(htmlpath, 'w', encoding='utf-8') as f:
                content = '<h2>{}</h2>'.format(path.stem)
                f.write(content)
                
            path.rename(site_path / (new_id+path.suffix))
    dump_csv(data, site_path / 'av.csv')

def add_fuliba():
    site_path = Path('/mnt/z/fuliba')
    site_path_temp = Path('/mnt/z/tmp/fuliba')
    data = read_csv(site_path / 'fuliba.csv')
    for path in site_path_temp.iterdir():
        new_id = str2md5(path.stem)
        num = 0
        for f in path.iterdir():
            if f.stem == path.stem:
                f.rename(path/(str(new_id)+".jpg"))
            else:
                num = num + 1
                f.rename(path/(new_id+'_'+str(num) + f.suffix))
        htmlpath = str(path)+'/'+new_id+'.html'
        with open(htmlpath, 'w', encoding='utf-8') as f:
            content = '<h2>{}</h2>'.format(path.stem)
            f.write(content)
        path.rename(site_path / new_id)
        data.append([new_id, path.stem, str(num)])
    dump_csv(data, site_path / "fuliba.csv")

def clean_qqmusic():
    site = Path('/mnt/z/qqmusic')
    data = []
    for path in site.iterdir():
        if path.suffix == ".mp3":
            new_id = str2md5(path.stem)
            data.append([new_id, path.stem])
            path.rename(path.parent / (new_id+path.suffix))
        else:
            new_id = str2md5(path.stem)
            path.rename(path.parent / (new_id+path.suffix))
    dump_csv(data, site / "qqmusic.csv")

def clean_fuliba():
    site = Path('/mnt/z/fuliba')
    data = []
    for path in site.iterdir():
        name = path.stem
        new_id = str2md5(name)
        num = 0
        for f in path.iterdir():
            if f.suffix == ".jpg" and f.stem != name:
                num = num + 1
                f.rename(f.parent / (new_id+'_'+str(num) + f.suffix))
            if f.suffix == ".jpg" and f.stem == name:
                f.rename(f.parent / (new_id + f.suffix))
        htmlpath = str(path)+'/'+new_id+'.html'
        with open(htmlpath, 'w', encoding='utf-8') as f:
            content = '<h2>{}</h2>'.format(path.stem)
            f.write(content)
        path.rename(path.parent / new_id)
        data.append([new_id, name, str(num)])
    dump_csv(data, site / "fuliba.csv")

def clean_epubee():
    site = Path('/mnt/z/epubee')
    data = []
    for path in site.iterdir():
        n1 = path.stem
        for f in path.iterdir():
            if f.suffix == ".epub":
                data.append([n1, f.stem])
    dump_csv(data, site / "epubee.csv")
    
def mkv2mp4(src, des):
    command = 'ffmpeg -i "{}" -c:v copy -c:a copy -c:s mov_text "{}"'.format(str(src), str(des))
    os.system(command)

def clean_vid():
    site = Path('/data/data/com.termux/files/home/temp/')
    data = read_csv("/data/data/com.termux/files/home/temp/vidinfo1.csv")
    for d in data:
        f = site / d[0]
        if d[1] == "h264_aac":
            mkv2mp4(f, f.parent.parent / 'result' / (f.stem + ".mp4"))
        # elif d[1] in ["h264_ac3","h264_pcm_s16le","h264_dts","h264_eac3"]:
        #     f = site / "1h264" / d[0]
        #     command = 'ffmpeg -i "{}" -c:v copy -c:a aac -c:s mov_text "{}"'.format(str(f), str(f.parent.parent / 'result' / (f.stem + ".mp4")))
        #     os.system(command)
        # elif d[1] in ["mpeg4_aac"]:
        #     f = site / "2aac" / d[0]
        #     command = 'ffmpeg -i "{}" -c:v libx264 -c:a copy -c:s mov_text "{}"'.format(str(f), str(f.parent.parent / 'result' / (f.stem + ".mp4")))
        #     os.system(command)
        elif d[1] in ["hevc_ac3","mpeg4_mp3","wmv3_wmapro","wmv3_wmav2"]:
            f = site / "hevc" / "3hevc" / d[0]
            if f.exists():
                command = 'ffmpeg -i "{}" -c:v libx264 -c:a aac -c:s mov_text "{}"'.format(str(f), str(f.parent.parent.parent / 'result' / (f.stem + ".mp4")))
                os.system(command)



if __name__ == "__main__":
    clean_vid()