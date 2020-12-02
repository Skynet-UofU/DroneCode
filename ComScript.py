''' 
Code Adapted from Dronekit's python examples and adapted to read from the Raspberry Pi's Serial Port
'''

from __future__ import print_function
import serial
import time
import re
from dronekit import connect, VehicleMode, LocationGlobalRelative

ser = serial.Serial("/dev/ttyAMA0", 57600)
print('Connecting to vehicle on: 127.0.0.1:14549')
vehicle = connect('127.0.0.1:14549')



def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute
    #   immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


cmds = vehicle.commands
cmds.download()
cmds.wait_ready()
print("Home position set")

# Display basic vehicle state
print (" Type: %s" % vehicle._vehicle_type)
print (" Armed: %s" % vehicle.armed)
print (" System status: %s" % vehicle.system_status.state)
print (" GPS: %s" % vehicle.gps_0)
print (" Alt: %s" % vehicle.location.global_relative_frame.alt)

# Continuous loop reading messages and handling commands
while True:
    received_data = ser.read()
    time.sleep(0.03)
    data_left = ser.inWaiting()
    received_data += ser.read(data_left)
    received_str = received_data.decode()
    if received_str.startswith("DRONE_CMD_TAKEOFF"):
        arm_and_takeoff(10)
    elif received_str.startswith("DRONE_CMD_GOTO"):
        lat = float(re.search("(?<=;).*(?=:)", received_str).group())
        lon = float(re.search("(?<=:)(.*)(?=DRONE_END)", received_str).group())
        if not vehicle.armed:
            arm_and_takeoff(10)
        print("Set default/target airspeed to 3")
        vehicle.airspeed = 3
        print("Going towards GPS point " + str(lat) + ", " + str(lon))
        point1 = LocationGlobalRelative(lat, lon, 20)
        vehicle.simple_goto(point1)
    elif received_str.startswith( "DRONE_CMD_RTH"):
        vehicle.mode = VehicleMode("RTL")
        print("returning home")
    elif received_str.startswith("DRONE_CMD_LAND"):
        vehicle.mode = VehicleMode("LAND")
    else :
        ser.write(received_data)
