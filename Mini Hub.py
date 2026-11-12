from pybricks.hubs import EssentialHub
from pybricks.pupdevices import UltrasonicSensor
from pybricks.parameters import Port
from pybricks.tools import wait, StopWatch
from pybricks.messaging import BLERadio

hub = EssentialHub()

# broadcasts distances on channel 2
radio = BLERadio(2, [1])

# change the port to wherever the distance sensor is plugged into the small hub
distance_right = UltrasonicSensor(Port.A)

last_broadcast = StopWatch()

while True:
    dist = distance_right.distance()  # millimetres

    if last_broadcast.time() >= 100:
        radio.broadcast(dist)
        last_broadcast.reset()

    wait(10)
