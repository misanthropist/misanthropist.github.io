#!/usr/bin/python3

import os
import threading 
import socket
import time
import cgi
import cgitb
# import face_recognition

cgitb.enable()
print("Content-type:text/html\n")
form = cgi.FieldStorage()
command = form.getvalue("command")

class Tello(object):
    def __init__(self):
        self.tello_ip = '192.168.10.1'
        self.command_port = 8889
        self.state_port = 8890
        self.video_port = 11111
        

        self.socket_command = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_command.bind(('', self.command_port))
        self.socket_video = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_video.bind(('', self.video_port))
        self.socket_state = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_state.bind(('', self.state_port))

        self.receive_command_thread = threading.Thread(target=self._receive_command_thread)
        self.receive_command_thread.daemon = True
        self.receive_command_thread.start()

        self.receive_state_thread = threading.Thread(target=self._receive_state_thread)
        self.receive_state_thread.daemon = True
        self.receive_state_thread.start()
        
        self.command_timeout = 3
        self.response = None
        self.state = None
        self.raw_pic = "."+os.path.sep+"temp"+os.path.sep+"h2640.jpeg"
        self.raw_vid = "."+os.path.sep+"temp"+os.path.sep+"h264"
        # self.face_location = (0,0,0,0)
        self.top = 220
        self.bottom = 330
        self.left= 330
        self.right = 440
        self.landoff_len = 220

        self.send_command("command")
    
    def __del__(self):
        self.socket_command.close()
        self.socket_state.close()
        self.socket_video.close()

    def _receive_command_thread(self):
        while True:
            try:
                self.response, ip = self.socket_command.recvfrom(1024)
                #print(self.response)
            except socket.error as e:
                print("Caught exception socket.error: {}".format(e))

    def _receive_state_thread(self):
        while True:
            try:
                self.state, ip = self.socket_state.recvfrom(1024)
                break
            except socket.error as e:
                print("Caught exception socket.error: {}".format(e))

    def send_command(self, command):
        self.socket_command.sendto(command.encode('utf-8'), (self.tello_ip, self.command_port))
        start = time.time()
        n = 0
        while self.response is None:
            time.sleep(0.1)
            n = n + 0.1
            if n > self.command_timeout:
                break
        dur = time.time()-start
        if self.response is None:
            response = 'none_response'
        else:
            response = self.response.decode('utf-8')
        self.response = None
        print((command, response, dur))
        return (command, response, dur)

    def takeoff(self):
        return self.send_command('takeoff')

    def land(self):
        return self.send_command('land')

    def emergency(self):
        return self.send_command('emergency')
    
    def read_state(self, command):
        """
        Args:
        command (str): speed?, battery?, time?, height?, temp?, attitude?, baro?, acceleration?, tof?, wifi?
        """
        return self.send_command("{}".format(command))
    
    def move(self, direction, distance=20):
        """Moves in a direction for a distance
        Args:
        direction (str): 'forword', 'back', 'right', 'left', 'up', 'down'
        distance (int): 20-500cm
        """
        return self.send_command('{} {}'.format(direction, distance))

    def rotate(self, direction='cw', degrees=90):
        """
        Args:
        direction (str): 'cw', 'ccw'
        degrees (int): 1-3600
        """
        return self.send_command('{} {}'.format(direction, degrees))
    
    def flip(self, direction='f'):
        """
        Args:
        direction (str): 'l', 'r', 'f', 'b'
        """
        return self.send_command('flip {}'.format(direction))

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
    
    def set_speed(self, speed=10):
        """
        Args:
        speed (int): 10-100cm/s
        """
        return self.send_command("speed {}".format(speed))
    
    def set_wifi(self, pwd):
        return self.send_command("wifi ssid {}".format(pwd))

    def streamoff(self):
        return self.send_command('streamoff')
    
    def streamon(self):
        return self.send_command('streamon')

    def record(self, command):
        with open('tello_commands', 'a') as f:
            f.write(command+',')

    def recall(self):
        with open('tello_commands', 'r') as f:
            commands = f.read().split(',')
        return commands

    def clear(self):
        with open('tello_commands', 'w') as f:
            f.write('')

    def get_pic(self):
        self.streamon()
        begin = time.time()
        packet_data = b""
        while True:
            try:
                res_string, ip = self.socket_video.recvfrom(2048)
                packet_data = b''.join([packet_data, res_string])
                dur = time.time()-begin
                if dur > 1:
                    with open(self.raw_vid, 'wb') as f:
                        f.write(packet_data)
                    os.system("ffmpeg -loglevel quiet -y -i {} -vf select='eq(pict_type\,I)' -vsync vfr {}".format(self.raw_vid, self.raw_pic))
                    # self.face_location = self.get_face_location(self.raw_pic)
                    break
            except socket.error as exc:
                print("Caught exception socket.error : %s" % exc)
    
    # def get_face_other(self, imgname):
    #     img = face_recognition.load_image_file(imgname)
    #     face_landmarks = face_recognition.face_landmarks(img)
    #     face_encoding = face_recognition.face_encodings(img)
    #     return face_landmarks, face_encoding


    # def get_face_location(self, imgname):
    #     top=bottom=left=right=0
    #     img = face_recognition.load_image_file(imgname)
    #     face_location = face_recognition.face_locations(img)
    #     face_num = len(face_location)
    #     if face_num > 0:
    #         top, right, bottom, left = face_location[0]
    #     return (top, bottom, left, right)

    def cruise(self):
        tello.get_pic()
        while True:
            tello.get_pic()
            time.sleep(4)
            # top,bottom,left,right = self.face_location
            print((top,bottom,left,right))
            if bottom-top > tello.landoff_len or top==bottom:
                self.emergency()
                break
            else:
                if top-tello.top > 10:
                    self.move('down')
                if tello.top-top >10:
                    self.move("up")
                if left-tello.left > 10:
                    self.move("right")
                if tello.left - left > 10:
                    self.move("left")
                if tello.landoff_len-(bottom-top) > 10:
                    self.move("forward")

start_time = time.time()
tello = Tello()

def run_command(command, record=True):
    if command == "takeoff":
        tello.takeoff()
        if record:
            tello.record(command)
    elif command == "land":
        tello.land()
        if record:
            tello.record(command)
    elif command == "emergency":
        tello.emergency()
        if record:
            tello.record(command)

    elif command == "speed":
        tello.read_state('speed?')
        if record:
            tello.record(command)
    elif command == "battery":
        tello.read_state('battery?')
        if record:
            tello.record(command)
    elif command == "height":
        tello.read_state('height?')
        if record:
            tello.record(command)
    elif command == "temp":
        tello.read_state('temp?')
        if record:
            tello.record(command)
    elif command == "state":
        print((command, tello.state))
        if record:
            tello.record(command)

    elif command == 'forward':
        tello.move('forward')
        if record:
            tello.record(command)
    elif command == 'back':
        tello.move('back')
        if record:
            tello.record(command)
    elif command == 'left':
        tello.move('left')
        if record:
            tello.record(command)
    elif command == 'right':
        tello.move('right')
        if record:
            tello.record(command)
    elif command == "up":
        tello.move("up")
        if record:
            tello.record(command)
    elif command == "down":
        tello.move('down')
        if record:
            tello.record(command)

    elif command == "flip":
        tello.flip()
        if record:
            tello.record(command)
    elif command == 'rotate':
        tello.rotate()
        if record:
            tello.record(command)
    elif command == "go":
        tello.go(20,20,20,10)
        if record:
            tello.record(command)
    elif command == "curve":
        tello.curve(20,0,0,0,20,0,10)
    elif command == 'recall':
        commands = tello.recall()
        for command in commands:
            run_command(command, False)
    elif command == "clear":
        tello.clear()
    elif command == "pic":
        tello.get_pic()
        # top,bottom,left,right = tello.face_location
        # print((top,bottom,left,right))
    elif command == 'cruise':
        tello.cruise()
    else:
        print("There is no such order")
    
    print("({}, {})".format(command, time.time()-start_time))

run_command(command)