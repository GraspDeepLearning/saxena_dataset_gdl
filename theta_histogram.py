
import h5py
import matplotlib.pyplot as plt
import numpy as np
import math

dataset = h5py.File('l_p_r_horizontal_patches_0_or_1.h5')

out_dataset = h5py.File('l_p_r_patches_pi_o_8.h5')


num_samples = dataset['xy_diff'].shape[0]

thetas = np.zeros((num_samples, 1))

for i in range(num_samples):
    x_diff = dataset['xy_diff'][i, 0]
    y_diff = dataset['xy_diff'][i, 1]
    thetas[i] = math.atan2(y_diff, x_diff)


num_thetas = 0
for i in range(num_samples):
    if thetas[i] < (math.pi/2.0 + math.pi/8.0) and thetas[i] > (math.pi/2.0-math.pi/8.0):
        num_thetas += 1

print
print 'num_thetas: ' + str(num_thetas)

out_dataset.create_dataset("rgbd_patches", (num_thetas, 72, 72, 4), maxshape=(None, 72, 72, 4), chunks=(10, 72, 72, 4))
out_dataset.create_dataset("rgbd_patch_labels", (num_thetas, 3), maxshape=(None, 3),  chunks=(1000, 3))
out_dataset.create_dataset("xy_diff", (num_thetas, 2), maxshape=(None, 2),  chunks=(1000, 2))

current_patch_index = 0
for i in range(num_samples):
    if thetas[i] < (math.pi/2.0 + math.pi/8.0) and thetas[i] > (math.pi/2.0-math.pi/8.0):
        out_dataset['rgbd_patches'][current_patch_index] = dataset['rgbd_patches'][i]
        out_dataset['rgbd_patch_labels'][current_patch_index] = dataset['rgbd_patch_labels'][i]
        out_dataset['xy_diff'][current_patch_index] = dataset['xy_diff'][i]
        current_patch_index += 1



xmin = -math.pi
xmax = math.pi
step = math.pi/4
y, x = np.histogram(thetas, bins=np.linspace(xmin, xmax, (xmax-xmin)/step))

nbins = y.size

plt.bar(x[:-1], y, width=x[1]-x[0], color='red', alpha=0.5)
plt.hist(thetas, bins=nbins, alpha=0.5)
plt.grid(True)
plt.show()
