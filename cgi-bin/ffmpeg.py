import glob
import os
import subprocess
import re

def genhls(filename):
    # os.system("ffmpeg -i {} -c:v libx264 -c:a aac -strict -2 -f hls -hls_time 8 -hls_list_size 0 {}.m3u8".format(filename, filename))
    os.system("ffmpeg -i {} -c:v copy -c:a copy -strict -2 -f hls -hls_time 8 -hls_list_size 0 {}.m3u8".format(filename, filename.split('.')[0]))
    
def get_format_info(filename):
    command = '''ffmpeg -i "{}" -hide_banner'''.format(filename)
    ffmpeger = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    info = str(ffmpeger.stderr.read())
    video_info = re.match(r'.*?Video: (.*?) ', info.replace('\n', '')).groups()
    audio_info = re.match(r'.*?Audio: (.*?) ', info.replace('\n', '')).groups()
    return (video_info[0], audio_info[0])

def get_keyframs_info(filename):
    command = "ffprobe -v error -skip_frame nokey -select_streams v:0 -show_entries frame=pkt_pts_time -of csv=print_section=0 {}".formate(filename)
    ffmpeger = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    return ffmpeger.stderr.read()

def gen_img(filename, imgdir):
    command = "ffmpeg -i {} {}".formate(filename, os.path.join(imgdir, 'image%d.jpg'))
    if not os.path.exists(imgdir):
        os.mkdir(imgdir)
    return os.system(command)

def cut(src, start, end, vformat, aformat, des):
    command = "ffmpeg -ss {} -t {} -i {} -c:v {} -c:a {} {}".formate(src, start, end,vformat, aformat, des)
    return os.system(command)

def get_stream(filename, audioname, stream="-vn"):
    command = "ffmpeg -i {} {} -c copy {}".format(filename, stream, audioname)
    return os.system(command)

def crop(src, x, y, des):
    command = "ffmpeg -i {} -vf crop=iw-{}:ih-{}:{}:{} {}".format(src, x, y, x, y, des)
    return os.system(command)

def overlay(src, x, y, des, logo):
    command = "ffmpeg -i {}  -vf 'movie={} [watermark]; [in][watermark] overlay={}:{} [out]' -c:v libx264 -c:a copy {}".format(src, logo, x, y, des)

def merge(src):
    flist = ''
    os.chdir(src)
    for f in sorted(glob.glob('*'), key=lambda x: int(x.split('.')[0])):
        flist += "file '"+f+"'\n"
    with open('flist.txt', 'w', encoding="utf-8") as f:
        f.write(flist)
 
    command = "ffmpeg -f concat -i {} -c copy {}".format(os.path.join('flist.txt'), os.path.join('..', src+'.mp4'))
    result = os.system(command)
    os.chdir('..')
    return result

def trans(src, vformat, aformat, des):
    command = "ffmpeg -i {} -c:v {} -c:a {} {}".format(src, vformat, aformat, des)
    return os.system(command)

def prt(filepath, start):
    coverpath = filepath[:-4]+'.jpg'
    command = 'ffmpeg -ss {} -i "{}" -frames:v 1 "{}"'.format(start, filepath, coverpath)
    return os.system(command)

def gen_keyframs(filename, imgdir):
    command = "ffmpeg -i {} -vf select='eq(pict_type\,I)' -vsync vfr {}".format(filename, os.path.join(imgdir, 'k%d.jpg'))
    if not os.path.exists(imgdir):
        os.mkdir(imgdir)
    return os.system(command)
