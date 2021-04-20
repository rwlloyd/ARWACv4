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