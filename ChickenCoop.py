import blynklib
from sense_hat import SenseHat
import RPi.GPIO as GPIO
import time
from time import sleep
BLYNK_AUTH = 'JtrGa9xCJSpPxot_VBifh1qxah8IysNE'
sense = SenseHat()
sense.clear()
from gpiozero import LED, Button
from signal import pause
from picamera import PiCamera
import datetime
import storeFileFB 


#initialise PiCamera
camera = PiCamera()


# initialize Blynk
blynk = blynklib.Blynk(BLYNK_AUTH)

#Determine GPIO pin mode as BCM
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) #turn off GPIO warnings 

#Initialising pins on the GPIO board

GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW) #external light
GPIO.setup(16, GPIO.OUT, initial=GPIO.LOW) #feeder
GPIO.setup(18, GPIO.OUT) #Door pin
GPIO.setup(21, GPIO.OUT, initial=GPIO.LOW) #internal light
GPIO.setup(20, GPIO.OUT, initial=GPIO.LOW) #heating


#Camera
@blynk.handle_event('write V7')
def write_gp_pin_handler(pin, value):
    frame = 1
    if value[0]=="1":
        print("Camera on")
        print (value)
        currentTime = datetime.datetime.now().strftime("%H:%M:%S")
        camera.rotation = 90        
        camera.start_preview()
        sleep(3)
        fileLoc = f'/home/pi/labs/week9/blynk/img/frame{frame}.jpg'
        camera.capture(fileLoc)
        camera.stop_preview()
        print(f'frame taken at {currentTime}') # print frame number to console
        storeFileFB.store_file(fileLoc)
        storeFileFB.push_db(fileLoc, currentTime)
        frame+=1
        

#setup PWM on pin 18 at 50Hz
pwm=GPIO.PWM(18, 50)
pwm.start(0)

@blynk.handle_event('write V3')
def write_gp_pin_handler(pin, value):
    print("initial GPIO 18")
    print('GP:'+ str(value))
    if value[0]=="1":
        print(value)
        pwm.ChangeDutyCycle(2)
    else:
        pwm.ChangeDutyCycle(12)


#Feeder control
@blynk.handle_event('write V6')
def write_gp_pin_handler(pin, value):
    print("initial GPIO 16")
    print('GP:'+ str(value))
    if value[0]=="0":
        print(value)
        GPIO.output(16, GPIO.HIGH)
    else:
        GPIO.output(16, GPIO.LOW)
 


#External light
@blynk.handle_event('write V1')
def write_gp_pin_handler(pin, value):
    print("initial GPIO 12")
    print('GP:'+ str(value))
    if value[0]=="0":
        print(value)
        GPIO.output(12, GPIO.HIGH)
    else:
        GPIO.output(12, GPIO.LOW)
 


#Internal lights
@blynk.handle_event('write V4')
def write_gp_pin_handler(pin, value):
    print("initial GPIO21")
    print('GP:'+ str(value))
    if value[0]=="0":
    	print(value)
    	GPIO.output(21, GPIO.HIGH)
    else:
    	GPIO.output(21, GPIO.LOW)
 
#heating control
@blynk.handle_event('write V5')
def write_gp_pin_handler(pin, value):
    print("initial GPIO 20")
    print('GP:'+ str(value))
    if value[0]=="0":
        print(value)
        GPIO.output(20, GPIO.HIGH)
    else:
        GPIO.output(20, GPIO.LOW)
 

# register handler for virtual pin V2(temperature) reading
@blynk.handle_event('read V2')
def read_virtual_pin_handler(pin):
    temp=round(sense.get_temperature(),2)
    if temp>17:
        print(temp)
        GPIO.output(20, GPIO.HIGH)
    else:
        GPIO.output(20, GPIO.LOW)
    
    print('V2 Read: ' + str(temp))  # print temp to console
    blynk.virtual_write(pin, temp)	


# infinite loop that waits for event
while True:
    blynk.run()
