# Implement the second move model for the Lego robot.
# The difference to the first implementation is:
# - added a scanner displacement
# - added a different start pose (measured in the real world)
# - result is now output to a file, as "F" ("filtered") records.
#
# 02_b_filter_motor_file
# Claus Brenner, 09 NOV 2012
from math import sin, cos, pi
from lego_robot import *

# This function takes the old (x, y, heading) pose and the motor ticks
# (ticks_left, ticks_right) and returns the new (x, y, heading).
def filter_step(old_pose, motor_ticks, ticks_to_mm, robot_width,
                scanner_displacement):

    curr_x, curr_y, curr_theta = old_pose
    ticks_left, ticks_right = map(lambda motor_ticks: motor_ticks*ticks_to_mm, motor_ticks)

    # Find out if there is a turn at all.
    if motor_ticks[0] == motor_ticks[1]:
        # No turn. Just drive straight.

        # --->>> Use your previous implementation.
        # Think about if you need to modify your old code due to the
        # scanner displacement?
        
        x = curr_x + ticks_left * cos(curr_theta)       # x' = x + lcos(Θ)
        y = curr_y + ticks_left * sin(curr_theta)       # y' = y + lsin(Θ)
        theta = curr_theta                              # Θ' = Θ
        
        return (x, y, theta)

    else:
        # Turn. Compute alpha, R, etc.

        # --->>> Modify your previous implementation.
        # First modify the the old pose to get the center (because the
        #   old pose is the LiDAR's pose, not the robot's center pose).
        alpha = (ticks_right - ticks_left)/robot_width
        R = ticks_left/alpha
        curr_x, curr_y = [i[0] - i[1] for i in zip([curr_x, curr_y], [i*(R + (robot_width/2)) for i in [sin(curr_theta), -cos(curr_theta)]])]
        curr_x = curr_x - scanner_displacement*(cos(curr_theta))
        curr_y = curr_y - scanner_displacement*sin(curr_theta)
        
        # Second, execute your old code, which implements the motion model
        #   for the center of the robot.
        theta = (curr_theta + alpha) % (2*pi)
        x, y = [sum(i) for i in zip([curr_x, curr_y] , [i*(R + (robot_width/2)) for i in [sin(theta), -1*cos(theta)]])]
        # Third, modify the result to get back the LiDAR pose from
        #   your computed center. This is the value you have to return.
        x = x + scanner_displacement*cos(theta)
        y = y + scanner_displacement*(sin(theta))

        return (x, y, theta)

if __name__ == '__main__':
    # Empirically derived distance between scanner and assumed
    # center of robot.
    scanner_displacement = 30.0

    # Empirically derived conversion from ticks to mm.
    ticks_to_mm = 0.349

    # Measured width of the robot (wheel gauge), in mm.
    robot_width = 150.0

    # Measured start position.
    pose = (1850.0, 1897.0, 213.0 / 180.0 * pi)

    # Read data.
    logfile = LegoLogfile()
    logfile.read("robot4_motors.txt")

    # Loop over all motor tick records generate filtered position list.
    filtered = []
    for ticks in logfile.motor_ticks:
        pose = filter_step(pose, ticks, ticks_to_mm, robot_width,
                           scanner_displacement)
        filtered.append(pose)

    # Write all filtered positions to file.
    f = open("poses_from_ticks.txt", "w")
    for pose in filtered:
        f.write("F %f %f %f \n" % pose)
    f.close()
