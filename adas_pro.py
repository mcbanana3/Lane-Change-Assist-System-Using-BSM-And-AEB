import RPi.GPIO as GPIO
import time
import statistics
import logging

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

logging.basicConfig(
    filename="adas_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

DIR = {
    "M1": (13,15),
    "M2": (18,16),
    "M3": (21,23),
    "M4": (26,24)
}

PWM_PINS = [11,12,19,22]

SENSORS = {
    "front": (5,6),
    "left": (17,27),
    "right": (20,25)
}

LED_RED = 10
LED_YELLOW = 9
LED_GREEN = 2
BUZZER = 3

for m in DIR.values():
    GPIO.setup(m[0], GPIO.OUT)
    GPIO.setup(m[1], GPIO.OUT)

for p in PWM_PINS:
    GPIO.setup(p, GPIO.OUT)

for trig, echo in SENSORS.values():
    GPIO.setup(trig, GPIO.OUT)
    GPIO.setup(echo, GPIO.IN)

for p in [LED_RED,LED_YELLOW,LED_GREEN,BUZZER]:
    GPIO.setup(p, GPIO.OUT)

PWM = [GPIO.PWM(pin,1000) for pin in PWM_PINS]

for p in PWM:
    p.start(0)

GPIO.output(LED_GREEN,True)

current_speed = 0

def set_speed(speed):
    global current_speed
    speed = max(0, min(100, int(speed)))
    current_speed = speed
    for p in PWM:
        p.ChangeDutyCycle(speed)

def set_dir(motor,state):
    GPIO.output(DIR[motor][0],state[0])
    GPIO.output(DIR[motor][1],state[1])

def forward(speed):
    set_speed(speed)
    for m in DIR:
        set_dir(m,(1,0))

def stop():
    global current_speed
    if current_speed <= 0:
        set_speed(0)
        return

    # Soft-stop ramp to reduce sudden braking
    for speed in range(current_speed, -1, -5):
        set_speed(speed)
        time.sleep(0.03)

    set_speed(0)

def lane_left():
    logging.info("Lane change LEFT")

    PWM[0].ChangeDutyCycle(30)
    PWM[1].ChangeDutyCycle(30)
    PWM[2].ChangeDutyCycle(80)
    PWM[3].ChangeDutyCycle(80)

    time.sleep(1)

def lane_right():
    logging.info("Lane change RIGHT")

    PWM[0].ChangeDutyCycle(80)
    PWM[1].ChangeDutyCycle(80)
    PWM[2].ChangeDutyCycle(30)
    PWM[3].ChangeDutyCycle(30)

    time.sleep(1)

def distance(trig,echo):

    vals=[]

    for _ in range(3):

        GPIO.output(trig,True)
        time.sleep(0.00001)
        GPIO.output(trig,False)

        start=time.time()
        timeout=start+0.04

        while GPIO.input(echo)==0 and time.time()<timeout:
            start=time.time()

        while GPIO.input(echo)==1 and time.time()<timeout:
            end=time.time()

        vals.append((end-start)*17150)

    return statistics.median(vals)

prev_front=100

def obstacle_prediction(current):

    global prev_front

    speed=prev_front-current

    prev_front=current

    return speed

try:

    print("ADAS PRO SYSTEM RUNNING")

    while True:

        front=distance(*SENSORS["front"])
        left=distance(*SENSORS["left"])
        right=distance(*SENSORS["right"])

        logging.info(f"Front:{front} Left:{left} Right:{right}")

        closing_rate=obstacle_prediction(front)

        if front>60:

            forward(80)

        elif front>40:

            forward(60)

        elif front>25:

            forward(40)

        elif front>20:

            forward(25)

        else:

            GPIO.output(LED_RED,True)
            GPIO.output(BUZZER,True)

            stop()

            time.sleep(0.5)

            if left>40:

                lane_left()

            elif right>40:

                lane_right()

            else:

                stop()

        if closing_rate>10:

            forward(30)

        time.sleep(0.1)

except KeyboardInterrupt:

    stop()

    GPIO.cleanup()