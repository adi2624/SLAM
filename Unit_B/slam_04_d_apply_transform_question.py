# For each cylinder in the scan, find its cartesian coordinates,
# in the world coordinate system.
# Find the closest pairs of cylinders from the scanner and cylinders
# from the reference, and the optimal transformation which aligns them.
# Then, use this transform to correct the pose.
# 04_d_apply_transform
# Claus Brenner, 14 NOV 2012
from lego_robot import *
from slam_b_library import filter_step
from slam_04_a_project_landmarks import\
     compute_scanner_cylinders, write_cylinders
from math import sqrt, atan2

# Given a list of cylinders (points) and reference_cylinders:
# For every cylinder, find the closest reference_cylinder and add
# the index pair (i, j), where i is the index of the cylinder, and
# j is the index of the reference_cylinder, to the result list.
# This is the function developed in slam_04_b_find_cylinder_pairs.

def compute_distance(p1,p2):

    x1,y1 = p1
    x2,y2 = p2
    return sqrt((x2-x1)**2 + (y2-y1)**2)

def find_cylinder_pairs(cylinders, reference_cylinders, max_radius):
    cylinder_pairs = []
    for i,cylinder in enumerate(cylinders):
        min_distance = float("inf")
        min_index = None
        for j,ref_cylinder in enumerate(reference_cylinders):
            dist = compute_distance(cylinder,ref_cylinder)
            if dist < min_distance:
                min_distance = dist
                min_index = j
        if min_distance < max_radius:
            cylinder_pairs.append((i,min_index))

    # --->>> Insert here your code from the last question,
    # slam_04_b_find_cylinder_pairs.

    return cylinder_pairs

# Given a point list, return the center of mass.
def compute_center(point_list):
    # Safeguard against empty list.
    if not point_list:
        return (0.0, 0.0)
    # If not empty, sum up and divide.
    sx = sum([p[0] for p in point_list])
    sy = sum([p[1] for p in point_list])
    return (sx / len(point_list), sy / len(point_list))

# Given a left_list of points and a right_list of points, compute
# the parameters of a similarity transform: scale, rotation, translation.
# If fix_scale is True, use the fixed scale of 1.0.
# The returned value is a tuple of:
# (scale, cos(angle), sin(angle), x_translation, y_translation)
# i.e., the rotation angle is not given in radians, but rather in terms
# of the cosine and sine.
def estimate_transform(left_list, right_list, fix_scale = False):
# Compute left and right center.
    lc = compute_center(left_list)
    rc = compute_center(right_list)
    for i in range(len(left_list)):
        left_list[i] = (left_list[i][0] - lc[0],left_list[i][1] - lc[1])
        right_list[i] = (right_list[i][0] - rc[0], right_list[i][1] - rc[1])
    left_centered = left_list
    right_centered = right_list
    cs = 0.0
    ss = 0.0
    rr = 0.0
    ll = 0.0
    m = len(left_list)
    for i in range(m):
        cs += (right_centered[i][0]*left_centered[i][0]) + (right_centered[i][1]*left_centered[i][1])
        ss += (-right_centered[i][0]*left_centered[i][1]) + (right_centered[i][1]*left_centered[i][0])
        rr += (right_centered[i][0]*right_centered[i][0]) + (right_centered[i][1]*right_centered[i][1])
        ll += (left_centered[i][0]*left_centered[i][0]) + (left_centered[i][1]*left_centered[i][1])

    if ll == 0.0 or rr == 0.0:
        return None
    if fix_scale:
        la = 1
    else:
        la = sqrt(rr/ll)
    
    if cs == 0.0 or ss == 0.0:
        return None
    else:
        c = cs/sqrt((cs*cs) + (ss*ss))
        s = ss/sqrt((cs*cs) + (ss*ss))

    rx = rc[0]
    ry = rc[1]

    lx = lc[0]
    ly = lc[1]

    tx = rx - (la)*(c*lx - s*ly)
    ty = ry - (la)*(s*lx + c*ly)

    # --->>> Insert here your code to compute lambda, c, s and tx, ty.

    return la, c, s, tx, ty

# Given a similarity transformation:
# trafo = (scale, cos(angle), sin(angle), x_translation, y_translation)
# and a point p = (x, y), return the transformed point.
def apply_transform(trafo, p):
    la, c, s, tx, ty = trafo
    lac = la * c
    las = la * s
    x = lac * p[0] - las * p[1] + tx
    y = las * p[0] + lac * p[1] + ty
    return (x, y)

# Correct the pose = (x, y, heading) of the robot using the given
# similarity transform. Note this changes the position as well as
# the heading.
def correct_pose(pose, trafo):
    
    # --->>> This is what you'll have to implement.
    x,y,theta = pose
    nx,ny = apply_transform(trafo,tuple((x,y)))
    c,s = trafo[1], trafo[2]
    alpha = atan2(s,c)
    ntheta = theta + alpha
    pose = [nx,ny,ntheta]

    return (pose[0], pose[1], pose[2])  # Replace this by the corrected pose.


if __name__ == '__main__':
    # The constants we used for the filter_step.
    scanner_displacement = 30.0
    ticks_to_mm = 0.349
    robot_width = 150.0

    # The constants we used for the cylinder detection in our scan.    
    minimum_valid_distance = 20.0
    depth_jump = 100.0
    cylinder_offset = 90.0

    # The maximum distance allowed for cylinder assignment.
    max_cylinder_distance = 400.0

    # The start pose we obtained miraculously.
    pose = (1850.0, 1897.0, 3.717551306747922)

    # Read the logfile which contains all scans.
    logfile = LegoLogfile()
    logfile.read("robot4_motors.txt")
    logfile.read("robot4_scan.txt")

    # Also read the reference cylinders (this is our map).
    logfile.read("robot_arena_landmarks.txt")
    reference_cylinders = [l[1:3] for l in logfile.landmarks]

    out_file = file("apply_transform.txt", "w")
    for i in xrange(len(logfile.scan_data)):
        # Compute the new pose.
        pose = filter_step(pose, logfile.motor_ticks[i],
                           ticks_to_mm, robot_width,
                           scanner_displacement)

        # Extract cylinders, also convert them to world coordinates.
        cartesian_cylinders = compute_scanner_cylinders(
            logfile.scan_data[i],
            depth_jump, minimum_valid_distance, cylinder_offset)
        world_cylinders = [LegoLogfile.scanner_to_world(pose, c)
                           for c in cartesian_cylinders]

        # For every cylinder, find the closest reference cylinder.
        cylinder_pairs = find_cylinder_pairs(
            world_cylinders, reference_cylinders, max_cylinder_distance)

        # Estimate a transformation using the cylinder pairs.
        trafo = estimate_transform(
            [world_cylinders[pair[0]] for pair in cylinder_pairs],
            [reference_cylinders[pair[1]] for pair in cylinder_pairs],
            fix_scale = True)

        # Transform the cylinders using the estimated transform.
        transformed_world_cylinders = []
        if trafo:
            transformed_world_cylinders =\
                [apply_transform(trafo, c) for c in
                 [world_cylinders[pair[0]] for pair in cylinder_pairs]]

        # Also apply the trafo to correct the position and heading.
        if trafo:
            pose = correct_pose(pose, trafo)

        # Write to file.
        # The pose.
        print >> out_file, "F %f %f %f" % pose
        # The detected cylinders in the scanner's coordinate system.
        write_cylinders(out_file, "D C", cartesian_cylinders)
        # The detected cylinders, transformed using the estimated trafo.
        write_cylinders(out_file, "W C", transformed_world_cylinders)

    out_file.close()
