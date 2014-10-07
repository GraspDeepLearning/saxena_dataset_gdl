
import traceback
import IPython

import os
import numpy as np
import h5py
import matplotlib.pyplot as plt
import scipy.ndimage

RAW_DATA_PATH = 'data'
PRIORS_DATA_FILE = 'priors.h5'


def get_rectangles(rect_filename):
    with open(rect_filename) as f:
        content = f.readlines()

    rectangles = []

    rect = []
    for line in content:
        split_line = line.split()

        rect.append((split_line[0], split_line[1]))
        if len(rect) == 4:
            rectangles.append(rect)
            rect = []

    return rectangles


def init_priors_dataset(datset_filename):
    prior_shape = (300, 300)
    dataset = h5py.File(datset_filename)

    dataset.create_dataset("l_gripper_given_palm", prior_shape)
    dataset.create_dataset("l_gripper_given_r_gripper", prior_shape)
    dataset.create_dataset("r_gripper_given_palm", prior_shape)
    dataset.create_dataset("r_gripper_given_l_gripper", prior_shape)
    dataset.create_dataset("palm_given_r_gripper", prior_shape)
    dataset.create_dataset("palm_given_l_gripper", prior_shape)

    return dataset


def blur_priors(dataset):

    keys = dataset.keys()

    for key in keys:
        blurred = scipy.ndimage.gaussian_filter(dataset[key], sigma=3)
        dataset[key + '_blur_norm'] = blurred / blurred.max()




def fill_priors(pos_rectangle_filename, dataset):

    l_gripper_given_palm = dataset["l_gripper_given_palm"]
    l_gripper_given_r_gripper = dataset["l_gripper_given_r_gripper"]
    r_gripper_given_palm = dataset["r_gripper_given_palm"]
    r_gripper_given_l_gripper = dataset["r_gripper_given_l_gripper"]
    palm_given_r_gripper = dataset["palm_given_r_gripper"]
    palm_given_l_gripper = dataset["palm_given_l_gripper"]

    prior_shape = l_gripper_given_palm.shape
    origin = np.array([prior_shape[0]/2.0, prior_shape[1]/2.0])

    for rectangle in get_rectangles(pos_rectangle_filename):

        print "rectangle: " + str(rectangle)
        if 'NaN' in rectangle[0] or 'NaN' in rectangle[1] or 'NaN' in rectangle[2] or 'NaN' in rectangle[3]:
            continue

        offset = np.array([-int((float(rectangle[0][1]) - float(rectangle[1][1]))/2.0),
                           -int((float(rectangle[0][0]) - float(rectangle[1][0]))/2.0)])

        #assume palm is at origin
        l_gripper_pose = origin - offset
        l_gripper_given_palm[l_gripper_pose[0], l_gripper_pose[1]] += 1

        r_gripper_pose = origin + offset
        r_gripper_given_palm[r_gripper_pose[0], r_gripper_pose[1]] += 1

        # assume r_gripper is at origin
        l_gripper_pose = origin - 2*offset
        l_gripper_given_r_gripper[l_gripper_pose[0], l_gripper_pose[1]] += 1

        palm_pose = origin - offset
        palm_given_r_gripper[palm_pose[0], palm_pose[1]] += 1

        #assume l_gripper is at origin
        r_gripper_pose = origin + 2*offset
        print r_gripper_pose
        r_gripper_given_l_gripper[r_gripper_pose[0], r_gripper_pose[1]] += 1

        palm_pose = origin + offset
        palm_given_l_gripper[palm_pose[0], palm_pose[1]] += 1


def main():
    try:
        files = []
        subdirs = os.listdir(RAW_DATA_PATH)
        for subdir in subdirs:
            for data_file in os.listdir(RAW_DATA_PATH + "/" + subdir):
                files.append(RAW_DATA_PATH + "/" + subdir + "/" + data_file)

        num_samples = 0
        for data_file in files:
            if '.png' in data_file:
                num_samples += 1

        if os.path.exists(PRIORS_DATA_FILE):
            os.remove(PRIORS_DATA_FILE)

        priors_dataset = init_priors_dataset()

        for data_file in files:
            if '.png' in data_file:

                file_root = data_file[:-5]
                pos_grasp_filename = str(file_root) + "cpos.txt"

                fill_priors(pos_grasp_filename, priors_dataset)

        blur_priors(priors_dataset)

    except Exception as e:
        traceback.print_exc(e)
        IPython.embed()


if __name__ == "__main__":
    main()





