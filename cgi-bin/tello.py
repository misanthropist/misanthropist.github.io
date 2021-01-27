#!/usr/bin/python3

import os
import threading 
import socket
import time
import cgi
import cgitb
import face_recognition

cgitb.enable()
print("Content-type:text/html\n")
form = cgi.FieldStorage()
command = form.getvalue("command")
start_time = time.time()

class Tello(object):
    def __init__(self):
        self.abort_flag = False
        self.command_timeout = 2
        self.response = None
        self.state = None
        self.tello_ip = '192.168.10.1'
        self.command_port = 8889
        self.state_port = 8890
        self.video_port = 11111
        self.raw_pic = "."+os.path.sep+"temp"+os.path.sep+"h264"
        self.face_location = ()
        self.top = 220
        self.bottom = 330
        self.left= 330
        self.right = 440
        self.landoff_len = 220
        
        self.socket_command = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_command.bind(('', self.command_port))
        self.socket_video = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_video.bind(('', self.video_port))
        self.socket_state = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_state.bind(('', self.state_port))

        self.receive_command_thread = threading.Thread(target=self._receive_command_thread)
        self.receive_command_thread.daemon = True
        self.receive_command_thread.start()

    def __del__(self):
        self.socket_command.close()
        self.socket_state.close()
        self.socket_video.close()

    def get_pic(self):
        # self.socket_command.sendto(b'streamon', (self.tello_ip, self.command_port))
        # print('sent: streamon')
        response = self.send_command('streamon')

        self.receive_video_thread = threading.Thread(target=self._receive_video_thread)
        self.receive_video_thread.daemon = True
        self.receive_video_thread.start()

        return response
    
    def get_face_other(self, imgname):
        img = face_recognition.load_image_file(imgname)
        face_landmarks = face_recognition.face_landmarks(img)
        face_encoding = face_recognition.face_encodings(img)
        return face_landmarks, face_encoding


    def get_face_location(self, imgname):
        top=bottom=left=right=0
        img = face_recognition.load_image_file(imgname)
        face_location = face_recognition.face_locations(img)
        face_num = len(face_location)
        if face_num > 0:
            top, right, bottom, left = face_location[0]
        # print("f:{}".format(face_location))
        return (top, bottom, left, right)

    def get_state(self):
        self.receive_state_thread = threading.Thread(target=self._receive_state_thread)
        self.receive_state_thread.daemon = True
        self.receive_state_thread.start()
        
    def _receive_command_thread(self):
        while True:
            try:
                self.response, ip = self.socket_command.recvfrom(1024)
                #print(self.response)
            except socket.error as e:
                print("Caught exception socket.error: {}".format(e))

    def _receive_video_thread(self):
        begin = time.time()
        packet_data = b""
        while True:
            try:
                res_string, ip = self.socket_video.recvfrom(2048)
                packet_data = b''.join([packet_data, res_string])
                dur = time.time()-begin
                if dur > 2:
                    with open(self.raw_pic, 'wb') as f:
                        print(dur)
                        f.write(packet_data)
                    os.system('ffmpeg -loglevel quiet -y -i {} -r 1 -f image2 {}.jpeg'.format(self.raw_pic, self.raw_pic))
                    self.face_location = self.get_face_location(self.raw_pic+'.jpeg')
                    begin = time.time()
                    packet_data = b""
            except socket.error as exc:
                print("Caught exception socket.error : %s" % exc)
    def _receive_state_thread(self):
        while True:
            try:
                self.state, ip = self.socket_state.recvfrom(1024)
                break
            except socket.error as e:
                print("Caught exception socket.error: {}".format(e))
    
    def set_abort_flag(self):
        self.abort_flag = True

    def send_command(self, command):
        self.abort_flag = False
        timer = threading.Timer(self.command_timeout, self.set_abort_flag)
        self.socket_command.sendto(command.encode('utf-8'), (self.tello_ip, self.command_port))

        timer.start()
        while self.response is None:
            if self.abort_flag is True:
                break
        timer.cancel()

        if self.response is None:
            response = 'none_response'
        else:
            response = self.response.decode('utf-8')
        self.response = None
        return (command, response)

    def start_command(self):
        return self.send_command("command")

    def takeoff(self):
        return self.send_command('takeoff')

    def land(self):
        return self.send_command('land')
    
    def rotate(self, direction='cw', degrees=90):
        """
        Args:
        direction (str): 'cw', 'ccw'
        degrees (int): 1-3600
        """
        return self.send_command('{} {}'.format(direction, degrees))
    
    def set_speed(self, speed=10):
        return self.send_command('speed {}'.format(speed))

    def flip(self, direction='f'):
        """
        Args:
        direction (str): 'l', 'r', 'f', 'b'
        """
        return self.send_command('flip {}'.format(direction))
    
    def move(self, direction, distance=20):
        """Moves in a direction for a distance
        Args:
        direction (str): 'forword', 'back', 'right', 'left', 'up', 'down'
        distance (int): 20-500cm
        """
        return self.send_command('{} {}'.format(direction, distance))
    
    def streamoff(self):
        return self.send_command('streamoff')

    def emergency(self):
        return self.send_command('emergency')

    def go(self, x, y, z, speed):
        """
        Args:
        x,y,z (int): 20-500cm
        speed (int): 10-100cm/s
        """
        return self.send_command('go {} {} {}'.format(x,y,z,speed))
    
    def curve(self, x1, y1, z1, x2, y2, z2, speed):
        """
        Args:
        x1,y1,z1,x2,y2,z2 (int): -500-500cm
        speed: 10-60cm/s
        坐标之差大于20
        """
        return self.send_command('curve {} {} {} {} {} {} {}'.format(x1,y1,z1,x2,y2,z2,speed))
    
    def speed(self, speed):
        """
        Args:
        speed (int): 10-100cm/s
        """
        return self.send_command("speed {}".format(speed))
    
    def wifi(self, pwd):
        return self.send_command("wifi ssid {}".format(pwd))

    def read_state(self, command):
        """
        Args:
        command (str): speed?, battery?, time?, height?, temp?, attitude?, baro?, acceleration?, tof?, wifi?
        """
        return self.send_command("{}".format(command))

    def cruise(self):
        print(tello.get_pic())
        while True:
            time.sleep(4)
            top,bottom,left,right = tello.face_location
            print(top,bottom,left,right)
            if bottom-top > tello.landoff_len or top==bottom:
                print("land")
                break
            else:
                if top-tello.top > 10:
                    print("down")
                if tello.top-top >10:
                    print("up")
                if left-tello.left > 10:
                    print("right")
                if tello.left - left > 10:
                    print("left")
                if tello.landoff_len-(bottom-top) > 10:
                    print("forward")

tello = Tello()
print(tello.start_command())

if command == "takeoff":
    print(tello.takeoff())
if command == "land":
    print(tello.land())
elif command == "pic":
    print(tello.get_pic())
    time.sleep(4)
    top,bottom,left,right = tello.face_location
    print(top,bottom,left,right)
elif command == "state":
    tello.get_state()
    time.sleep(1)
    print(tello.state)
elif command == "flip":
    print(tello.flip())
elif command == 'forward':
    print(tello.move('forward'))
elif command == 'back':
    print(tello.move('back'))
elif command == 'left':
    print(tello.move('left'))
elif command == 'right':
    print(tello.move('right'))
elif command == 'rotate':
    print(tello.rotate())
elif command == "down":
    print(tello.move('down'))
elif command == "up":
    print(tello.move("up"))
elif command == "go":
    print(tello.go(20,20,20,10))
elif command == 'cruise':
    tello.cruise()

print("{}, {}".format(command, time.time()-start_time))