
import traceback
import IPython

import os
import numpy as np
import h5py
import matplotlib.pyplot as plt
import scipy.ndimage

RAW_DATA_PATH = 'data'
PRIORS_DATA_FILE = 'priors.h5'



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


def save_priors(dataset):
    keys = dataset.keys()

    for key in keys:
        plt.imsave('priors/' + key + '.png', dataset[key])


def fill_priors(dataset):

    input_dataset = h5py.File('l_p_r_patches_pi_o_8.h5')

    l_gripper_given_palm = dataset["l_gripper_given_palm"]
    l_gripper_given_r_gripper = dataset["l_gripper_given_r_gripper"]
    r_gripper_given_palm = dataset["r_gripper_given_palm"]
    r_gripper_given_l_gripper = dataset["r_gripper_given_l_gripper"]
    palm_given_r_gripper = dataset["palm_given_r_gripper"]
    palm_given_l_gripper = dataset["palm_given_l_gripper"]

    prior_shape = l_gripper_given_palm.shape
    origin = np.array([prior_shape[0]/2.0, prior_shape[1]/2.0])

    print input_dataset.keys()
    xy_diffs = input_dataset['xy_diff']

    for offset in xy_diffs:

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

        if os.path.exists(PRIORS_DATA_FILE):
            os.remove(PRIORS_DATA_FILE)

        priors_dataset = init_priors_dataset(PRIORS_DATA_FILE)

        fill_priors(priors_dataset)

        blur_priors(priors_dataset)

        save_priors(priors_dataset)

    except Exception as e:
        traceback.print_exc(e)
        IPython.embed()


if __name__ == "__main__":
    main()





