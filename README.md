# DroneCode
This program connects to a MAVLINK packet stream in this case outputted by mavproxy locally at 127.0.0.1:14549 as well as the primary UART port on a Rapsberry PI. Here messages sent over LORA radios are decoded as message streams or drone commands. Messages are read then sent back onto the network through the radio. Drone commands are read and handled as such using the Dronekit Python API. 
###
Drone Command Formatting
DRONE_CMD_GOTO;{ID};{lat}:{lon}DRONE_END
DRONE_CMD_{command};{}DRONE_END where command = {TAKEOFF, LAND, RTH}
