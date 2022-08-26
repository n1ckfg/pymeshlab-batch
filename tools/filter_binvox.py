# https://github.com/raahii/3dgan-chainer/blob/master/binvox_to_h5.py
# https://github.com/raahii/3dgan-chainer/blob/master/LICENSE
# Convert dataset(.binvox) to numpy array in advance
# to load dataset more efficient.

import sys, os, glob
import numpy as np
import scipy.ndimage as nd
import binvox_rw

# filters
dilateReps = 1 #3
sobelReps = 0 #0
gaussianSigma = 0 #0
medianSize = 4 #3
laplaceReps = 0 #0
erodeReps = 1 #2

def read_binvox(path, fix_coords=True):
    voxel = None
    with open(path, 'rb') as f:
        voxel = binvox_rw.read_as_3d_array(f, fix_coords)
    return voxel

def write_binvox(data, url):
    with open(url, 'wb') as f:
        data.write(f)

def main():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] # get all args after "--"

    inputPath = argv[0]
    dims = int(argv[1])

    for fileName in os.listdir(inputPath):
        if fileName.endswith(".binvox"): 
            inputUrl = os.path.join(inputPath, fileName)

            print("Reading from: " + inputUrl)
            bv = read_binvox(inputUrl)

            outputUrl = ""
            outputPathArray = inputUrl.split(".")
            for i in range(0, len(outputPathArray)-1):
                outputUrl += outputPathArray[i]
            outputUrl += "_filter.binvox"
           
            # filters
            if (dilateReps > 0):
                print("Dilating...")
                for i in range(0, dilateReps):
                    nd.binary_dilation(bv.data.copy(), output=bv.data)

            if (sobelReps > 0):
                print ("Sobel filter...")
                for i in range(0, sobelReps):
                    nd.sobel(bv.data.copy(), output=bv.data)

            if (gaussianSigma > 0):
                print("Gaussian filter")
                nd.gaussian_filter(bv.data.copy(), sigma=gaussianSigma, output=bv.data)
            
            if (medianSize > 0):
                print("Median filter")
                nd.median_filter(bv.data.copy(), size=medianSize, output=bv.data)
            
            if (laplaceReps > 0):
                print("Laplace filter...")
                for i in range(0, laplaceReps):
                    nd.laplace(bv.data.copy(), output=bv.data)

            if (erodeReps > 0):
                print("Eroding...")
                for i in range(0, erodeReps):
                    nd.binary_erosion(bv.data.copy(), output=bv.data)

            print("Writing to: " + outputUrl)
            write_binvox(bv, outputUrl)
    
main()