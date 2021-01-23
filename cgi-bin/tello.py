import os
import threading 
import socket
import time
import cgi
import cgitb

cgitb.enable()
print("Content-type:text/html\n")
form = cgi.FieldStorage()
command = form.getvalue("command")
start_time = time.time()

class Tello(object):
    def __init__(self):
        self.abort_flag = False
        self.command_timeout = 3
        self.response = None
        self.state = None
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
                    raw_name = "."+os.path.sep+"temp"+os.path.sep+"h264"
                    with open(raw_name, 'wb') as f:
                        print(dur)
                        f.write(packet_data)
                    os.system('ffmpeg -loglevel quiet -y -i {} -r 1 -f image2 {}.jpeg'.format(raw_name, raw_name))
                    begin = time.time()
                    packet_data = b""
            except socket.error as exc:
                print("Caught exception socket.error : %s" % exc)
    def _receive_state_thread(self):
        while True:
            try:
                self.state, ip = self.socket_state.recvfrom(1024)
                print(self.state)
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
    
    def rotate_cw(self, degrees=10):
        return self.send_command('cw {}'.format(degrees))
    
    def set_speed(self, speed=10):
        return self.send_command('speed {}'.format(speed))

    def flip(self, direction='f'):
        return self.send_command('flip {}'.format(direction))
    
    def move(self, direction, distance):
        return self.send_command('{} {}'.format(direction, distance))
    

tello = Tello()
print(tello.start_command())

if command == "takeoff":
    print(tello.takeoff())
elif command == "pic":
    print(tello.get_pic())
elif command == "state":
    print(tello.get_state())
elif command == "flip":
    print(tello.flip())
elif command == 'forward':
    print(tello.move('forward', 20))
elif command == 'back':
    print(tello.move('back', 20))
elif command == 'left':
    print(tello.move(left, 20))
elif command == 'right':
    print(tello.move('right', 20))
elif command == 'rotate':
    print(tello.rotate_cw())

time.sleep(4)
print("{}, {}".format(command, time.time()-start_time))