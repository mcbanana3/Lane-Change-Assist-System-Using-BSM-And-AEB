import RPi.GPIO as GPIO
import time
import keyboard

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# FRONT DRIVER (Driver 1)
ENA1 = 18
IN1 = 23
IN2 = 24

ENB1 = 19
IN3 = 25
IN4 = 8

# BACK DRIVER (Driver 2)
ENA2 = 12
IN5 = 16
IN6 = 20

ENB2 = 13
IN7 = 21
IN8 = 26

# Setup pins
pins = [ENA1, IN1, IN2, ENB1, IN3, IN4,
        ENA2, IN5, IN6, ENB2, IN7, IN8]

for pin in pins:
    GPIO.setup(pin, GPIO.OUT)

# PWM setup
pwm_front_left  = GPIO.PWM(ENA1, 1000)
pwm_front_right = GPIO.PWM(ENB1, 1000)
pwm_back_left   = GPIO.PWM(ENA2, 1000)
pwm_back_right  = GPIO.PWM(ENB2, 1000)

pwm_front_left.start(0)
pwm_front_right.start(0)
pwm_back_left.start(0)
pwm_back_right.start(0)

speed = 70

##################################################
# FORWARD
##################################################
def forward():
    print("Forward")

    pwm_front_left.ChangeDutyCycle(speed)
    pwm_front_right.ChangeDutyCycle(speed)
    pwm_back_left.ChangeDutyCycle(speed)
    pwm_back_right.ChangeDutyCycle(speed)

    # Front motors forward
    GPIO.output(IN1, True)
    GPIO.output(IN2, False)

    GPIO.output(IN3, True)
    GPIO.output(IN4, False)

    # Back motors forward
    GPIO.output(IN5, True)
    GPIO.output(IN6, False)

    GPIO.output(IN7, True)
    GPIO.output(IN8, False)


##################################################
# BACKWARD
##################################################
def backward():
    print("Backward")

    pwm_front_left.ChangeDutyCycle(speed)
    pwm_front_right.ChangeDutyCycle(speed)
    pwm_back_left.ChangeDutyCycle(speed)
    pwm_back_right.ChangeDutyCycle(speed)

    # Front motors backward
    GPIO.output(IN1, False)
    GPIO.output(IN2, True)

    GPIO.output(IN3, False)
    GPIO.output(IN4, True)

    # Back motors backward
    GPIO.output(IN5, False)
    GPIO.output(IN6, True)

    GPIO.output(IN7, False)
    GPIO.output(IN8, True)


##################################################
# LEFT TURN
##################################################
def left():
    print("Left")

    # Front wheels turn left (slow or reverse)
    pwm_front_left.ChangeDutyCycle(0)
    pwm_front_right.ChangeDutyCycle(speed)

    # Back wheels forward
    pwm_back_left.ChangeDutyCycle(speed)
    pwm_back_right.ChangeDutyCycle(speed)

    # Front left stop
    GPIO.output(IN1, False)
    GPIO.output(IN2, False)

    # Front right forward
    GPIO.output(IN3, True)
    GPIO.output(IN4, False)

    # Back forward
    GPIO.output(IN5, True)
    GPIO.output(IN6, False)

    GPIO.output(IN7, True)
    GPIO.output(IN8, False)


##################################################
# RIGHT TURN
##################################################
def right():
    print("Right")

    pwm_front_left.ChangeDutyCycle(speed)
    pwm_front_right.ChangeDutyCycle(0)

    pwm_back_left.ChangeDutyCycle(speed)
    pwm_back_right.ChangeDutyCycle(speed)

    # Front left forward
    GPIO.output(IN1, True)
    GPIO.output(IN2, False)

    # Front right stop
    GPIO.output(IN3, False)
    GPIO.output(IN4, False)

    # Back forward
    GPIO.output(IN5, True)
    GPIO.output(IN6, False)

    GPIO.output(IN7, True)
    GPIO.output(IN8, False)


##################################################
# STOP
##################################################
def stop():
    print("Stop")

    pwm_front_left.ChangeDutyCycle(0)
    pwm_front_right.ChangeDutyCycle(0)
    pwm_back_left.ChangeDutyCycle(0)
    pwm_back_right.ChangeDutyCycle(0)


print("Keyboard Control Ready")
print("W Forward")
print("S Backward")
print("A Left")
print("D Right")
print("SPACE Stop")
print("Q Quit")

try:

    while True:

        if keyboard.is_pressed('w'):
            forward()

        elif keyboard.is_pressed('s'):
            backward()

        elif keyboard.is_pressed('a'):
            left()

        elif keyboard.is_pressed('d'):
            right()

        elif keyboard.is_pressed('space'):
            stop()

        elif keyboard.is_pressed('q'):
            break

        time.sleep(0.1)

except KeyboardInterrupt:
    pass

GPIO.cleanup()
