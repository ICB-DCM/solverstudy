# script to compute a linear regression given the data points (x_i,y_i)
# attention: the data in the .tsv file must not be in log scale or negative values will crash the linear regression

import numpy as np


def linearRegression(tsv_file, x_catagory, y_catagory):

    if len(tsv_file[x_catagory]) != len(tsv_file[y_catagory]):
        print('Error: Length of categories does not match!')

    # take those num_x and num_p where 'error_message' == nan
    x_data_point = []
    y_data_point = []
    for iCount in range(0, len(tsv_file[x_catagory])):
        if tsv_file[x_catagory][iCount] != 0 and tsv_file[y_catagory][iCount] != 0:
            x_data_point.append(np.log10(tsv_file[x_catagory][iCount]))
            y_data_point.append(np.log10(tsv_file[y_catagory][iCount]))

    Num_data_points = len(x_data_point)
    x_data_point = np.asarray(x_data_point)
    y_data_point = np.asarray(y_data_point)

    # solve linear system of equations Ax = c
    A = np.asarray([[Num_data_points, sum(x_data_point)], [sum(x_data_point), sum(x_data_point*x_data_point)]])
    c = np.asarray([[sum(y_data_point)],[sum(x_data_point*y_data_point)]])
    A_inv = np.linalg.inv(A)

    numerical_solution = A_inv.dot(c)
    a = numerical_solution[0]
    b = numerical_solution[1]

    ################## only for comparison ##################
    x_data_point_bio = []
    y_data_point_bio = []
    for iCount in range(0, 27):
        if tsv_file[x_catagory][iCount] != 0 and tsv_file[y_catagory][iCount] != 0:
            x_data_point_bio.append(np.log10(tsv_file[x_catagory][iCount]))
            y_data_point_bio.append(np.log10(tsv_file[y_catagory][iCount]))

    Num_data_points_bio = len(x_data_point_bio)
    x_data_point_bio = np.asarray(x_data_point_bio)
    y_data_point_bio = np.asarray(y_data_point_bio)

    # solve linear system of equations Ax = c
    A_bio = np.asarray([[Num_data_points_bio, sum(x_data_point_bio)], [sum(x_data_point_bio), sum(x_data_point_bio * x_data_point_bio)]])
    c_bio = np.asarray([[sum(y_data_point_bio)], [sum(x_data_point_bio * y_data_point_bio)]])
    A_inv_bio = np.linalg.inv(A_bio)

    numerical_solution = A_inv_bio.dot(c_bio)
    d = numerical_solution[0]
    e = numerical_solution[1]

    return a,b
