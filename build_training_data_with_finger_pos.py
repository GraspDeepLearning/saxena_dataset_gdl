
import traceback
import IPython

import os
import math
import numpy as np
import h5py
import matplotlib.pyplot as plt
import scipy.ndimage

RAW_DATA_PATH = 'data'
OUTPUT_DATA_FILE = 'palm_and_finger_patches_l_p_r.h5'


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



def fill_rgbd(rgb_filename, pcd_filename, rgbd_data, current_sample_index):

    rgbd_data[current_sample_index, :, :, 0:3] = plt.imread(rgb_filename)

    with open(pcd_filename) as f:
        content = f.readlines()

    for line in content:
        split_line = line.split()
        if len(split_line) == 5:
            depth = split_line[2]
            index = int(split_line[-1])
            row = math.floor(index/640)
            col = (index % 640)
            rgbd_data[current_sample_index, row, col, 3] = float(depth)

    #normalize depth data
    rgbd_data[current_sample_index, :, :, 3] = rgbd_data[current_sample_index, :, :, 3]/rgbd_data[current_sample_index, :, :, 3].max()


def fill_patches(rectangle_filename, rgbd_data, rgbd_patches, rgbd_patch_labels, current_sample_index, current_patch_index, patch_label_value):
    for rectangle in get_rectangles(rectangle_filename):
        try:
            x_coord = int((float(rectangle[0][1]) + float(rectangle[1][1]) + float(rectangle[2][1]) + float(rectangle[3][1]))/4)
            y_coord = int((float(rectangle[0][0]) + float(rectangle[1][0]) + float(rectangle[2][0]) + float(rectangle[3][0]))/4)
            x_diff = -int((float(rectangle[0][1]) - float(rectangle[1][1]))/2.0)
            y_diff = -int((float(rectangle[0][0]) - float(rectangle[1][0]))/2.0)

        except:
            return current_patch_index

        # add the data sample for the center of the gripper
        rgbd_patches[current_patch_index] = rgbd_data[current_sample_index, x_coord-36:x_coord+36, y_coord-36:y_coord+36]
        rgbd_patch_labels[current_patch_index] = (-patch_label_value, patch_label_value, -patch_label_value)

        current_patch_index += 1
        rgbd_patches.resize((current_patch_index + 1, 72, 72, 4))
        rgbd_patch_labels.resize((current_patch_index + 1, 3))

        #add the data sample for the left gripper
        rgbd_patches[current_patch_index] = rgbd_data[current_sample_index, x_coord-x_diff-36:x_coord-x_diff+36, y_coord-y_diff-36:y_coord-y_diff+36]
        rgbd_patch_labels[current_patch_index] = (patch_label_value, -patch_label_value, -patch_label_value)

        current_patch_index += 1
        rgbd_patches.resize((current_patch_index + 1, 72, 72, 4))
        rgbd_patch_labels.resize((current_patch_index + 1, 3))

        #add the data sample for the right gripper
        rgbd_patches[current_patch_index] = rgbd_data[current_sample_index, x_coord+x_diff-36:x_coord+x_diff+36, y_coord+y_diff-36:y_coord+y_diff+36]
        rgbd_patch_labels[current_patch_index] = (-patch_label_value, -patch_label_value, patch_label_value)

        current_patch_index += 1
        rgbd_patches.resize((current_patch_index + 1, 72, 72, 4))
        rgbd_patch_labels.resize((current_patch_index + 1, 3))

    return current_patch_index


def extract_raw():
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

        if os.path.exists(OUTPUT_DATA_FILE):
           os.remove(OUTPUT_DATA_FILE)

        dataset = h5py.File(OUTPUT_DATA_FILE)

        dataset.create_dataset("rgbd_data", (num_samples, 480, 640, 4), chunks=(10, 480, 640, 4))
        dataset.create_dataset("rgbd_patches", (1, 72, 72, 4), maxshape=(None, 72, 72, 4), chunks=(10, 72, 72, 4))
        dataset.create_dataset("rgbd_patch_labels", (1, 3), maxshape=(None, 3),  chunks=(1000, 3))
        dataset.create_dataset("finger_labels", (1, 3))
        dataset["finger_labels"] = ["l_gripper", "palm", "r_gripper"]

        rgbd_data = dataset["rgbd_data"]
        rgbd_patches = dataset["rgbd_patches"]
        rgbd_patch_labels = dataset["rgbd_patch_labels"]

        current_sample_index = 0
        current_patch_index = 0

        for data_file in files:
            if '.png' in data_file:

                print str(current_sample_index) + "/" + str(num_samples)

                file_root = data_file[:-5]

                rgb_filename = data_file
                pcd_filename = str(file_root) + ".txt"
                pos_grasp_filename = str(file_root) + "cpos.txt"
                neg_grasp_filename = str(file_root) + "cneg.txt"

                fill_rgbd(rgb_filename, pcd_filename, rgbd_data, current_sample_index)
                current_patch_index = fill_patches(pos_grasp_filename, rgbd_data, rgbd_patches, rgbd_patch_labels, current_sample_index, current_patch_index, 1)
                current_patch_index = fill_patches(neg_grasp_filename, rgbd_data, rgbd_patches, rgbd_patch_labels, current_sample_index, current_patch_index, -1)

                current_sample_index += 1


    except Exception as e:
        traceback.print_exc(e)
        IPython.embed()


if __name__ == "__main__":
    extract_raw()





