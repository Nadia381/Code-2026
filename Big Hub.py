from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor
from pybricks.parameters import Button, Port
from pybricks.tools import wait, StopWatch
from pybricks.iodevices import PUPDevice
from pybricks.messaging import BLERadio

import umath

hub = PrimeHub()

# broadcasts ball data on channel 1, listens for small hub distances on channel 2
radio = BLERadio(1, [2])

sensor = PUPDevice(Port.F)  # IR Ring - change port if needed

# Motor initialization (B | A over C | D)
MotorA = Motor(Port.A)
MotorB = Motor(Port.B)
MotorC = Motor(Port.C)
MotorD = Motor(Port.D)

# Local distance sensor (big hub)
distance_left = UltrasonicSensor(Port.E)


def forward(speed):
    MotorA.dc(speed)
    MotorB.dc(-speed)
    MotorC.dc(-speed)
    MotorD.dc(speed)


def right(speed):
    MotorA.dc(-speed)
    MotorB.dc(-speed)
    MotorC.dc(speed)
    MotorD.dc(speed)


def left(speed):
    MotorA.dc(speed)
    MotorB.dc(speed)
    MotorC.dc(-speed)
    MotorD.dc(-speed)


def back(speed):
    MotorA.dc(-speed)
    MotorB.dc(speed)
    MotorC.dc(speed)
    MotorD.dc(-speed)


def orbit(ball_direction, ball_strength):
    # Gives the best direction to move
    if ball_direction == 12:
        return 12
    if ball_strength < 75:
        return ball_direction
    if ball_direction == 0:
        return -1
    return (ball_direction + 0.5) % 12


def move(direction, speed, heading):
    # if you don't want yaw correction, input 0 for heading
    # input 1 - 12 for direction
    direction *= 30
    if direction != -1:
        motora = speed * umath.sin(umath.radians(direction + 45)) - heading * 0.7
        motorb = speed * umath.sin(umath.radians(direction - 45)) - heading * 0.7
        motorc = speed * umath.sin(umath.radians(direction - 135)) - heading * 0.7
        motord = speed * umath.sin(umath.radians(direction + 135)) - heading * 0.7
    else:
        # only yaw correction, no translation
        motora = motorb = motorc = motord = 0

    # clamp max duty cycle to -100 to 100
    scale = 100 / max(umath.fabs(motora), umath.fabs(motorb),
                      umath.fabs(motorc), umath.fabs(motord), 100.0)
    motora *= scale
    motorb *= scale
    motorc *= scale
    motord *= scale

    MotorA.dc(motora)
    MotorB.dc(motorb)
    MotorC.dc(motorc)
    MotorD.dc(motord)


hub.imu.reset_heading(0)
speed = 0
# assuming 12 is forward

last_broadcast = StopWatch()
last_print = StopWatch()

while True:
    # Handle buttons
    for btn in hub.buttons.pressed():
        if btn == Button.LEFT:
            hub.imu.reset_heading(0)
        elif btn == Button.RIGHT:
            if speed == 300:
                speed = 0
                wait(100)
            else:
                speed = 300
                wait(100)

    # Update sensors
    values = sensor.read(5)
    direction = values[1]
    strength = values[0]

    yaw1 = hub.imu.heading()
    yaw = -yaw1

    move_dir = orbit(direction, strength)
    move(move_dir, speed, yaw)

    # distance reading from the small hub (channel 2), or None if nothing heard yet
    dist_from_small = radio.observe(2)

    # Broadcast ball data + yaw to the other hub, at most every 100 ms
    if last_broadcast.time() >= 100:
        radio.broadcast((direction, strength, yaw))
        last_broadcast.reset()

    # print at most every 500 ms so the loop stays fast
    if last_print.time() >= 500:
        print(f"dir: {direction}, str: {strength}, small dist: {dist_from_small}")
        last_print.reset()
