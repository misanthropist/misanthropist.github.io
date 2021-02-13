#!/usr/bin/python3

import RPi.GPIO as GPIO
import cgi
import time
import os
import cgitb
from Adafruit_PWM_Servo_Driver import PWM
import json

cgitb.enable()
print("Content-type:text/html\n")
form = cgi.FieldStorage()
command = form.getvalue("command")

SensorLeft = 12
T_SensorLeft = 13
SensorRight = 16
PassiveBuzzer = 17
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
    pwm = PWM(0x40, debug=True)
    pwm.setPWMFreq(50)
    write(pwm, servonum, angle)
    time.sleep(1)
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
    def __init__(self):
        self.Buzz = GPIO.PWM(PassiveBuzzer, 440)
        self.song = [330, 393, 441, 330, 294, 330, 393, 441, 525, 441, 393, 262, 330, 294, 294, 330, 393, 294, 330, 330, 211, 211, 211, 262, 294, 330, 294, 248, 211, 262, 196]
        self.beat = [1, 1, 3, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1,1, 3, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1]
    def sing(self):
        self.Buzz.start(50)
        for i in range(len(self.song)):
            self.Buzz.ChangeFrequency(self.song[i])
            time.sleep(self.beat[i]*0.5)
    def destory(self):
        self.Buzz.stop()

class Movement(object):
    def __init__(self):
        self.L_Motor = GPIO.PWM(PWMA, 100)
        self.L_Motor.start(0)
        self.R_Motor = GPIO.PWM(PWMB, 100)
        self.R_Motor.start(0)

    def forword(self, speed=50):
        self.L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2,False)
        GPIO.output(AIN1,True) 

        self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2,False)
        GPIO.output(BIN1,True) 

    def stop(self):
        self.L_Motor.ChangeDutyCycle(0)
        GPIO.output(AIN2,False)
        GPIO.output(AIN1,False) 

        self.R_Motor.ChangeDutyCycle(0)
        GPIO.output(BIN2,False)
        GPIO.output(BIN1,False) 

    def backword(self, speed=50):
        self.L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2,True)
        GPIO.output(AIN1,False) 

        self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2,True)
        GPIO.output(BIN1,False) 

    def left(self, speed=50):
        self.L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2,True)
        GPIO.output(AIN1,False) 

        self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2,False)
        GPIO.output(BIN1,True) 

    def right(self, speed=50):
        self.L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2,False)
        GPIO.output(AIN1,True) 

        self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2,True)
        GPIO.output(BIN1,False) 
    
    def destory(self):
        self.L_Motor.stop()
        self.R_Motor.stop()

class Infrared(object):
    def __init__(self):
        pass
    def state(self):
        if GPIO.input(SensorLeft) == True and GPIO.input(SensorRight) == True:
            return "11"
        elif GPIO.input(SensorLeft) == True and GPIO.input(SensorRight) == False:
            return "10"
        elif GPIO.input(SensorLeft) == False and GPIO.input(SensorRight) == True:
            return "01"
        else:
            return "00"
    def destory(self):
        GPIO.cleanup()


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
       self.mjpg_streamer = 'mjpg_streamer -i "input_uvc.so -d /dev/video0" -o "output_http.so -w www -p 8080" /dev/null 2>&1 &'
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
        self.arm2 = 4
        self.arm3 = 5
        self.arm4 = 6
        self.angles = {
            "horizontal": 60,
            "vertical": 0,
            "ultrasonic": 72,
            "arm1": 0,
            "arm2": 0,
            "arm3": 0,
            "arm4": 0
        }

    def get_angles(self):
        with open('angles', 'r') as f:
            self.angles = json.load(f)
        return self.angles

    def set_angles(self):
        with open('angles', 'w') as f:
            json.dump(self.angles, f)

    def ultrasonic_rotate(self):
        self.angles = self.get_angles()
        self.angles["ultrasonic"] = self.angles["ultrasonic"] + 18
        if self.angles["ultrasonic"] >= 180:
            self.angles["ultrasonic"] = 0
        rotate(self.ultrasonic, self.angles["ultrasonic"])
        self.set_angles()
    
    def horizontal_rotate(self):
        self.angles = self.get_angles()
        self.angles["horizontal"] = self.angles["horizontal"] + 18
        if self.angles["horizontal"] >= 180:
            self.angles["horizontal"] = 0
        rotate(self.horizontal, self.angles["horizontal"])
        self.set_angles()

    def vertical_rotate(self):
        self.angles = self.get_angles()
        self.angles["vertical"] = self.angles["vertical"] + 18
        if self.angles["vertical"] >= 90:
            self.angles["vertical"] = 0
        rotate(self.vertical, self.angles["vertical"])
        self.set_angles()
    
    def base_rotate(self):
        self.angles = self.get_angles()
        self.angles["arm1"] = self.angles["arm1"]+10
        if self.angles["arm1"] >= 180:
            self.angles["arm1"] = 0
        rotate(self.arm1, self.angles["arm1"])
        self.set_angles()
    
    def left_rotate(self):
        self.angles = self.get_angles()
        self.angles["arm2"] = self.angles["arm2"]+10
        if self.angles["arm2"] >= 180:
            self.angles["arm2"] = 0
        rotate(self.arm2, self.angles["arm2"])
        self.set_angles()
        
    def right_rotate(self):
        self.angles = self.get_angles()
        self.angles["arm3"] = self.angles["arm3"]+10
        if self.angles["arm3"] >= 180:
            self.angles["arm3"] = 0
        rotate(self.arm3, self.angles["arm3"])
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
            if distance() < 40:
                right()
                time.sleep(1.5)
            if distance() < 10:
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

buzzer = Buzzer()
movement = Movement()
infrared = Infrared()
ultrasonic = Ultrasonic()
webcam = Webcam()
servo = Servo()
cruise = Cruise()


def run_command(command, record=True):
    start = time.time()
    if command == "forword":
        movement.forword()
        time.sleep(3)
        if record:
            cruise.record(command)
    elif command == "backword":
        movement.backword()
        time.sleep(3)
        if record:
            cruise.record(command)
    elif command == "left":
        movement.left()
        time.sleep(0.1)
        if record:
            cruise.record(command)
    elif command == "right":
        movement.right()
        time.sleep(0.1)
        if record:
            cruise.record(command)
    elif command == "stop":
        movement.stop()
        # movement.destory()
        if record:
            cruise.record(command)
    elif command == "sing":
        buzzer.sing()
        buzzer.destory()
    elif command == "infrared":
        n = 30
        while n:
            state = infrared.state()
            print(state)
            time.sleep(0.1)
            n = n - 1
    elif command == "ultrasonic":
        n = 30
        while n:
            distance = ultrasonic.distance()
            print(distance)
            time.sleep(0.1)
            n = n - 1
    elif command == "webcam_on":
        webcam.webcam_on()
    elif command == "webcam_off":
        webcam.webcam_off()
    elif command == "restore":
        servo.set_angles()
        servo.ultrasonic_rotate()
        servo.horizontal_rotate()
        servo.vertical_rotate()
    elif command == "servo0":
        servo.ultrasonic_rotate()
    elif command == "servo1":
        servo.horizontal_rotate()
    elif command == "servo2":
        servo.vertical_rotate()
    elif command == "cruise":
        cruise.auto(infrared.state, ultrasonic.distance, movement.forword, movement.backword, movement.left, movement.right, movement.stop)
    elif command == "servo3":
        servo.base_rotate()
    elif command == "servo4":
        servo.left_rotate()
    elif command == "servo5":
        servo.right_rotate()
    elif command == "servo6":
        servo.claw_rotate()
    elif command == "recall":
        commands = cruise.recall()
        for command in commands:
            run_command(command, False)
    elif command == "clear":
        cruise.clear()
    else:
        print("There is no such order")

    print("{}, {}".format(command, time.time()-start))


run_command(command)
GPIO.cleanup()
