#!/usr/bin/python3

import RPi.GPIO as GPIO
import cgi
import time
import os
import cgitb
from Adafruit_PWM_Servo_Driver import PWM
import json
import car_music_dataset as d
from pi_dashboard import init_val

cgitb.enable()
print("Content-type:text/html\n")
form = cgi.FieldStorage()
command = form.getvalue("command")

PassiveBuzzer = 17
SensorLeft = 12
T_SensorLeft = 13
SensorRight = 16
PWMA = 18
TRIG = 20
ECHO = 21
AIN1 = 22
PWMB = 23
BIN2 = 24
BIN1 = 25
T_SensorRight = 26
AIN2 = 27

def setServoPulse(pwm, channel, pulse):
    pulseLength = 1000000.0/50.0/4096.0
    pulse = pulse*1000.0/pulseLength
    pwm.setPWM(channel, 0, int(pulse))

def write(pwm, servonum, x):
    y = x/90.0+0.5
    y = max(y, 0.5)
    y = min(y, 2.5)
    setServoPulse(pwm, servonum, y)

def rotate(servonum, angle=90):
    pwm = PWM(0x40, debug=False)
    pwm.setPWMFreq(50)
    write(pwm, servonum, angle)
    # time.sleep(0.1)
    # PWM(0x40, debug=True)

def setup():
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(PassiveBuzzer, GPIO.OUT)

    GPIO.setup(AIN2,GPIO.OUT)
    GPIO.setup(AIN1,GPIO.OUT)
    GPIO.setup(PWMA,GPIO.OUT)

    GPIO.setup(BIN1,GPIO.OUT)
    GPIO.setup(BIN2,GPIO.OUT)
    GPIO.setup(PWMB,GPIO.OUT)

    GPIO.setup(SensorLeft, GPIO.IN)
    GPIO.setup(SensorRight, GPIO.IN)

    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)


class Buzzer(object):
    def __init__(self, song):
        self.Buzz = GPIO.PWM(PassiveBuzzer, 440)
        self.freqs = [d.note2freq[d.num2note[num]] for num in song["nums"]]
        self.beats = song["beats"]
    def sing(self):
        self.Buzz.start(50)
        for i in range(len(self.freqs)):
            self.Buzz.ChangeFrequency(self.song[i])
            time.sleep(self.beats[i])
    def destory(self):
        self.Buzz.stop()

class Movement(object):
    def __init__(self):
        self.L_Motor = GPIO.PWM(PWMA, 100)
        self.L_Motor.start(0)
        self.R_Motor = GPIO.PWM(PWMB, 100)
        self.R_Motor.start(0)

    def stop(self, dur=0.1):
        self.L_Motor.ChangeDutyCycle(0)
        GPIO.output(AIN2,False)
        GPIO.output(AIN1,False)

        self.R_Motor.ChangeDutyCycle(0)
        GPIO.output(BIN2,False)
        GPIO.output(BIN1,False)
        time.sleep(dur)

    def forword(self, speed=30, dur=0.5):
        self.L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2,False)
        GPIO.output(AIN1,True)

        self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2,False)
        GPIO.output(BIN1,True)
        time.sleep(dur)

    def backword(self, speed=30, dur=0.5):
        self.L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2,True)
        GPIO.output(AIN1,False)

        self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2,True)
        GPIO.output(BIN1,False)
        time.sleep(dur)

    def left(self, speed=50, dur=0.1):
        self.L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2,True)
        GPIO.output(AIN1,False)

        self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2,False)
        GPIO.output(BIN1,True)
        time.sleep(dur)

    def right(self, speed=50, dur=0.1):
        self.L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2,False)
        GPIO.output(AIN1,True)

        self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2,True)
        GPIO.output(BIN1,False)
        time.sleep(dur)
    
    def destory(self):
        self.L_Motor.stop()
        self.R_Motor.stop()

class Ultrasonic(object):
    def __init__(self):
        pass

    def distance(self):
        GPIO.output(TRIG, 0)
        time.sleep(0.000002)

        GPIO.output(TRIG, 1)
        time.sleep(0.00001)
        GPIO.output(TRIG, 0)

        while GPIO.input(ECHO) == 0:
            pass
        t1 = time.time()
        while GPIO.input(ECHO) == 1:
            pass
        t2 = time.time()
        dis = (t2-t1)*340*100/2
        return dis

    def destory(self):
        GPIO.cleanup()

class Webcam(object):
    def __init__(self):
       self.mjpg_streamer = '/home/doudou/temp/mjpg/mjpg_streamer -i "/home/doudou/temp/mjpg/input_uvc.so -d /dev/video0 -n -f 1 -r 160x120" -o "/home/doudou/temp/mjpg/output_http.so -w /home/doudou/temp/mjpg/www -p 8080" > /dev/null 2>&1 &'
       self.close_mjpg = 'mjpg=`pidof mjpg_streamer` && kill -9 $mjpg'
    def webcam_on(self):
        os.system(self.mjpg_streamer)
    def webcam_off(self):
        os.system(self.close_mjpg)

class Servo(object):
    def __init__(self):
        self.horizontal = 1
        self.vertical = 2
        self.ultrasonic = 0
        self.arm1 = 3
        self.arm2 = 5
        self.arm3 = 4
        self.arm4 = 6
        self.angles = {
            "ultrasonic": 73,
            "horizontal": 70,
            "vertical": 0,
            "arm1": 80,
            "arm2": 90,
            "arm3": 0,
            "arm4": 0
        }
        self.base_angles = {
            "ultrasonic": 73,
            "horizontal": 70,
            "vertical": 0,
            "arm1": 80,
            "arm2": 100,
            "arm3": 50,
            "arm4": 0
        }

    def get_angles(self):
        with open('angles', 'r') as f:
            self.angles = json.load(f)
        return self.angles

    def set_angles(self, isBase=False):
        if isBase:
            angles = self.base_angles
        else:
            angles = self.angles
        with open('angles', 'w') as f:
            json.dump(angles, f)

    def ultrasonic_rotate(self, angle=10, mode='ccw'):
        self.angles = self.get_angles()
        if mode == 'ccw':
            self.angles["ultrasonic"] = self.angles["ultrasonic"] + angle
        elif mode == 'cw':
            self.angles["ultrasonic"] = self.angles["ultrasonic"] - angle
        if self.angles["ultrasonic"] >= 180 or self.angles['ultrasonic'] <=0:
            self.angles["ultrasonic"] = 73
        rotate(self.ultrasonic, self.angles["ultrasonic"])
        self.set_angles()
    
    def horizontal_rotate(self, angle=10, mode='ccw'):
        self.angles = self.get_angles()
        if mode == 'ccw':
            self.angles["horizontal"] = self.angles["horizontal"] + angle
        elif mode == 'cw':
            self.angles["horizontal"] = self.angles["horizontal"] - angle
        if self.angles["horizontal"] >= 180 or self.angles["horizontal"] <=0:
            self.angles["horizontal"] = 70
        rotate(self.horizontal, self.angles["horizontal"])
        self.set_angles()

    def vertical_rotate(self, angle=10, mode='ccw'):
        self.angles = self.get_angles()
        if mode == 'ccw':
            self.angles["vertical"] = self.angles["vertical"] + angle
        elif mode == 'cw':
            self.angles["vertical"] = self.angles["vertical"] - angle
        if self.angles["vertical"] >= 90 or self.angles["vertical"] <=0:
            self.angles["vertical"] = 0
        rotate(self.vertical, self.angles["vertical"])
        self.set_angles()
    
    def init_ultrasonic_camera(self):
        self.set_angles(isBase=True)
        self.ultrasonic_rotate()
        time.sleep(0.1)
        self.horizontal_rotate()
        time.sleep(0.1)
        self.vertical_rotate()
        time.sleep(0.1)

    def camera_walk(self):
        self.restore()
        self.horizontal_rotate(angle=60, mode='cw')
        time.sleep(0.1)
        for i in range(30):
            self.horizontal_rotate(angle=5)
            time.sleep(0.5)
        self.restore()
        self.vertical_rotate(angle=40)
        time.sleep(0.1)
        self.horizontal_rotate(angle=60, mode='cw')
        time.sleep(0.1)
        for i in range(30):
            self.horizontal_rotate(angle=5)
            time.sleep(0.5)
        self.init_ultrasonic_camera()

    def init_arms(self):
        rotate(self.arm1, 80)
        time.sleep(0.1)
        for i in range(10, 110, 10):
            rotate(self.arm2, i)
            time.sleep(0.1)
            rotate(self.arm3, abs(i-130))
            time.sleep(0.1)
        self.angles["arm1"] = 80
        self.angles["arm2"] = 100
        self.angles["arm3"] = 30
        self.set_angles()
    
    def close_arms(self):
        rotate(self.arm1, 80)
        time.sleep(0.1)
        rotate(self.arm2, 100)
        time.sleep(0.1)
        for i in range(10, 150, 10):
            rotate(self.arm3, i)
            time.sleep(0.1)
        for i in range(90, 0, -10):
            rotate(self.arm2, i)
            time.sleep(0.1)
        self.angles["arm1"] = 80
        self.angles["arm2"] = 140
        self.angles["arm3"] = 10
        self.set_angles()

    def base_rotate(self, angle=10, mode='ccw'):
        self.angles = self.get_angles()
        if mode == 'ccw':
            self.angles["arm1"] = self.angles["arm1"]+angle
        elif mode == 'cw':
            self.angles["arm1"] = self.angles["arm1"] - angle
        if self.angles["arm1"] >= 180 or self.angles["arm1"] <= 0:
            self.angles["arm1"] = 80
        rotate(self.arm1, self.angles["arm1"])
        self.set_angles()
    
    def left_rotate(self, angle=10, mode='ccw'):
        self.angles = self.get_angles()
        if mode == 'ccw':
            self.angles["arm3"] = self.angles["arm3"] +angle
        elif mode == 'cw':
            self.angles["arm3"] = self.angles["arm3"] - angle
        if self.angles["arm3"] >= 150 or self.angles ['arm3']<= 0:
            self.angles["arm3"] = 30
        rotate(self.arm3, self.angles["arm3"])
        self.set_angles()
        
    def right_rotate(self, angle=10, mode='ccw'):
        self.angles = self.get_angles()
        if mode == 'ccw':
            self.angles["arm2"] = self.angles["arm2"] + angle
        if mode == 'cw':
            self.angles["arm2"] = self.angles["arm2"]-angle
        if self.angles["arm2"] >= 180 or self.angles["arm2"] <= 100:
            self.angles["arm2"] = 100
        rotate(self.arm2, self.angles["arm2"])
        self.set_angles()

    def claw_rotate(self):
        self.angles = self.get_angles()
        self.angles["arm4"] = self.angles["arm4"]+10
        if self.angles["arm4"] >= 60:
            self.angles["arm4"] = 0
        rotate(self.arm4, self.angles["arm4"])
        self.set_angles()

class Cruise(object):
    def __init__(self):
        pass

    def auto(self, state, distance, forword, backword, left, right, stop):
        while True:
            if state() == "00":
                backword()
            if state() == "11":
                forword()
            if state() == "01":
                right()
                time.sleep(0.3)
            if state() == "10":
                left()
                time.sleep(0.3)
            if distance() < 10:
                stop()
                servo.restore()
                servo.ultrasonic_rotate(angle=60)
                time.sleep(0.1)
                if distance() > 40:
                    right()
                    time.sleep(0.3)
                    servo.restore()
                else:
                    servo.restore()
                    servo.ultrasonic_rotate(angle=60, mode="cw")
                    time.sleep(0.1)
                    if distance() > 40:
                        left()
                        time.sleep(0.3)
                        servo.restore()
                    else:
                        stop()
                        break
    
    def record(self, command):
        with open('commands', 'a') as f:
            f.write(command+',')
    
    def recall(self):
        with open('commands', 'r') as f:
            commands = f.read().split(',')
        return commands
    
    def clear(self):
        with open('commands', 'w') as f:
            f.write('')


setup()

shanghaitan = Buzzer(d.shanghaitan)
movement = Movement()
ultrasonic = Ultrasonic()
webcam = Webcam()
servo = Servo()
cruise = Cruise()


def run_command(command):
    start = time.time()
    if command == "shanghaitan":
        shanghaitan.sing()
    elif command == "forword":
        movement.forword()
    elif command == "backword":
        movement.backword()
    elif command == "left":
        movement.left()
    elif command == "right":
        movement.right()

    elif command == "ultrasonic":
        distance = ultrasonic.distance()
        print(distance)
    elif command == "webcam_on":
        webcam.webcam_on()
    elif command == "webcam_off":
        webcam.webcam_off()

    elif command == "init_ultrasonic_camera":
        servo.init_ultrasonic_camera()
    elif command == "ultrasonic_ccw":
        servo.ultrasonic_rotate()
    elif command == "ultrasonic_cw":
        servo.ultrasonic_rotate(mode='cw')
    elif command == "camera_hccw":
        servo.horizontal_rotate()
    elif command == "camera_vccw":
        servo.vertical_rotate()
    elif command == "camera_hcw":
        servo.horizontal_rotate(mode='cw')
    elif command == "camera_vcw":
        servo.vertical_rotate(mode='cw')
    elif command == "camera_walk":
        servo.camera_walk()

    elif command == "servo3":
        servo.base_rotate()
    elif command == "servo4":
        servo.right_rotate()
    elif command == "servo5":
        servo.left_rotate()
    elif command == "arm1cw":
        servo.base_rotate(mode='cw')
    elif command == "arm2cw":
        servo.right_rotate(mode='cw')
    elif command == "arm3cw":
        servo.left_rotate(mode='cw')
    elif command == "servo6":
        servo.claw_rotate()
    elif command == "init_arms":
        servo.init_arms()
    elif command == "close_arms":
        servo.close_arms()
    elif command == "recall":
        commands = cruise.recall()
        while True:
            for command in commands:
                run_command(command, False)
                time.sleep(0.5)
                if ultrasonic.distance() < 10:
                    movement.stop()
                    break
            if ultrasonic.distance() < 10:
                movement.stop()
                break
    elif command == "state":
        print(init_val)

    print("{}, {}".format(command, time.time()-start))

run_command(command)
# pwm = PWM(0x40, debug=False)
GPIO.cleanup()
