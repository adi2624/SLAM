# Implement the first move model for the Lego robot.
# 02_a_filter_motor
# Claus Brenner, 31 OCT 2012
from math import sin, cos, pi
from pylab import *
from lego_robot import *

# This function takes the old (x, y, heading) pose and the motor ticks
# (ticks_left, ticks_right) and returns the new (x, y, heading).
def filter_step(old_pose, motor_ticks, ticks_to_mm, robot_width):

    curr_x, curr_y, curr_theta = old_pose
    ticks_left, ticks_right = map(lambda motor_ticks: motor_ticks*ticks_to_mm, motor_ticks)

    # Find out if there is a turn at all.
    if motor_ticks[0] == motor_ticks[1]:
        # No turn. Just drive straight.

        # --->>> Implement your code to compute x, y, theta here.

        x = curr_x + ticks_left * cos(curr_theta)       # x' = x + lcos(Θ)
        y = curr_y + ticks_left * sin(curr_theta)       # y' = y + lsin(Θ)
        theta = curr_theta                              # Θ' = Θ

        return (x, y, theta)

    else:
        # Turn. Compute alpha, R, etc.

        alpha = (ticks_right - ticks_left)/robot_width
        R = ticks_left/alpha
        curr_x, curr_y = [i[0] - i[1] for i in zip([curr_x, curr_y], [i*(R + (robot_width/2)) for i in [sin(curr_theta), -cos(curr_theta)]])]
        theta = (curr_theta + alpha) % (2*pi)
        x, y = [sum(i) for i in zip([curr_x, curr_y] , [i*(R + (robot_width/2)) for i in [sin(theta), -1*cos(theta)]])]

        # --->>> Implement your code to compute x, y, theta here.
        return (x, y, theta)

if __name__ == '__main__':
    # Empirically derived conversion from ticks to mm.
    ticks_to_mm = 0.349

    # Measured width of the robot (wheel gauge), in mm.
    robot_width = 150.0

    # Read data.
    logfile = LegoLogfile()
    logfile.read("robot4_motors.txt")

    # Start at origin (0,0), looking along x axis (alpha = 0).
    pose = (0.0, 0.0, 0.0)

    # Loop over all motor tick records generate filtered position list.
    filtered = []
    for ticks in logfile.motor_ticks:
       # import pdb; pdb.set_trace()
        pose = filter_step(pose, ticks, ticks_to_mm, robot_width)
        print(pose)
        filtered.append(pose)

    # Draw result.
    for pose in filtered:
        plot([p[0] for p in filtered], [p[1] for p in filtered], 'bo')
    show()
