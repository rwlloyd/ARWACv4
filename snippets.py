# Sketchy? ackermann code 

# def calculateVelocities(vehicleLength: float, vehicleWidth: float, velocity, angle):
#     # Appl Sci 2017, 7, 74
#     if angle > 0: #turn Left
#         R = vehicleLength/math.tan(angle)
#         v1 = velocity*(1-(vehicleWidth/R))
#         v2 = velocity*(1+(vehicleWidth/R))
#         v3 = velocity*((R-(vehicleWidth/2)/R))
#         v4 = velocity*((R+(vehicleWidth/2)/R))
#     elif angle < 0: #turn Right
#         R = vehicleLength/math.tan(angle)
#         v1 = velocity*(1+(vehicleWidth/R))
#         v2 = velocity*(1-(vehicleWidth/R))
#         v3 = velocity*((R+(vehicleWidth/2)/R))
#         v4 = velocity*((R-(vehicleWidth/2)/R))
#     elif angle < 0.001 and angle > -0.001:
#         angle = 0
#         v1 = velocity
#         v2 = velocity
#         v3 = velocity
#         v4 = velocity

#     if sum([v1, v2, v3, v4]) < 4.00:
#         return v1, v2, v3, v4
#     else:
#         raise ValueError(f'Velocity value incorrect: {v1}, {v2}, {v3}, {v4} Angle {angle} Sum: {sum([v1, v2, v3, v4])}')

import socket
host = "192.168.0.28" # Device IP
port = 28000 # IP port
PACKET_SIZE=1024 # how many characters to read at a time
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect((host,port)) #connect to the device



print("host: " + str(host) + " port: " + str(port) + " packet size: " + str(PACKET_SIZE))



import pynmea2 # parses nmea data to readable format ## https://github.com/Knio/pynmea2



while True: # continuously read and handle data
data = str(sock.recv(PACKET_SIZE))[2:][:-5 ] ## [2:][:-5 ] removes excess characters from data string
#print(data) # prints raw data stream
message = pynmea2.parse(str(data))
print("Timestamp UTC: " + str(message.timestamp) + " Latitude: " + str(message.latitude) + " Longitude: " + str(message.longitude))