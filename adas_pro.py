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

BLIND_SPOT_WARN_CM = 25
LANE_CONFIRM_MIN_CM = 20

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

def set_speed_ramped(target_speed, step=5, delay=0.03):
    global current_speed
    target_speed = max(0, min(100, int(target_speed)))

    if target_speed == current_speed:
        return

    if target_speed > current_speed:
        for speed in range(current_speed, target_speed + 1, step):
            set_speed(speed)
            time.sleep(delay)
    else:
        for speed in range(current_speed, target_speed - 1, -step):
            set_speed(speed)
            time.sleep(delay)

def set_dir(motor,state):
    GPIO.output(DIR[motor][0],state[0])
    GPIO.output(DIR[motor][1],state[1])

def forward(speed):
    set_speed_ramped(speed)
    for m in DIR:
        set_dir(m,(1,0))

def stop():
    set_speed_ramped(0)

def beep_warning(pulses=2, on_time=0.05, off_time=0.05):
    for _ in range(pulses):
        GPIO.output(BUZZER, True)
        time.sleep(on_time)
        GPIO.output(BUZZER, False)
        time.sleep(off_time)

def beep_caution():
    # Slow beep for caution
    beep_warning(pulses=1, on_time=0.12, off_time=0.12)

def beep_emergency():
    # Fast beeps for emergency
    beep_warning(pulses=3, on_time=0.04, off_time=0.04)

def confirm_front_clear():
    front = distance(*SENSORS["front"])
    logging.info(f"Front confirm:{front}")
    return front > LANE_CONFIRM_MIN_CM

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

            GPIO.output(BUZZER, False)

        elif front>25:

            forward(40)

            beep_caution()

        elif front>20:

            forward(25)

            beep_caution()

        else:

            GPIO.output(LED_RED,True)

            beep_emergency()

            stop()

            time.sleep(0.5)

            if closing_rate < 0:
                logging.info("Lane change blocked: front improving")
                stop()

            elif left>40:

                lane_left()

                if not confirm_front_clear():
                    stop()
                    time.sleep(0.2)

            elif right>40:

                lane_right()

                if not confirm_front_clear():
                    stop()
                    time.sleep(0.2)

            else:

                stop()

        if closing_rate>10:

            forward(30)

        if current_speed > 0 and (left < BLIND_SPOT_WARN_CM or right < BLIND_SPOT_WARN_CM):
            beep_warning()

        time.sleep(0.1)

except KeyboardInterrupt:

    stop()

    GPIO.cleanup()