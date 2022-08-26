'''
MIT License

Copyright (c) 2015 Dena Bazazian

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from pyntcloud import PyntCloud 
import numpy as np
from mpl_toolkits.mplot3d import Axes3D 
import matplotlib.pyplot as plt 
import pandas as pd
import os
import sys
import pdb

argv = sys.argv
argv = argv[argv.index("--") + 1:] # get all args after "--"
inputPath = argv[0]

for fileName in os.listdir(inputPath):
    if fileName.endswith("_resample.ply"): 
        url = os.path.join(inputPath, fileName)
        
        outputPath = ""
        outputPathArray = url.split(".")
        for i in range(0, len(outputPathArray)-1):
            outputPath += outputPathArray[i]
        outputPath += "_edges.ply"

        pcd1 = PyntCloud.from_file(url)
            
        # define hyperparameters
        k_n = 40 # 50
        thresh = 0.08 # 0.03

        pcd_np = np.zeros((len(pcd1.points),6))

        # find neighbors
        kdtree_id = pcd1.add_structure("kdtree")
        k_neighbors = pcd1.get_neighbors(k=k_n, kdtree=kdtree_id) 

        # calculate eigenvalues
        ev = pcd1.add_scalar_field("eigen_values", k_neighbors=k_neighbors)

        x = pcd1.points['x'].values 
        y = pcd1.points['y'].values 
        z = pcd1.points['z'].values 

        e1 = pcd1.points['e3('+str(k_n+1)+')'].values
        e2 = pcd1.points['e2('+str(k_n+1)+')'].values
        e3 = pcd1.points['e1('+str(k_n+1)+')'].values

        sum_eg = np.add(np.add(e1,e2),e3)
        sigma = np.divide(e1,sum_eg)
        sigma_value = sigma

        # visualize the edges
        sigma = sigma>thresh

        '''
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # visualize the edges
        img = ax.scatter(x, y, z, c=sigma, cmap='jet')

        fig.colorbar(img) 
        plt.show() 
        '''

        # Save the edges and point cloud
        thresh_min = sigma_value < thresh
        sigma_value[thresh_min] = 0
        thresh_max = sigma_value > thresh
        sigma_value[thresh_max] = 255

        pcd_np[:,0] = x
        pcd_np[:,1] = y
        pcd_np[:,2] = z
        pcd_np[:,3] = sigma_value

        edge_np = np.delete(pcd_np, np.where(pcd_np[:,3] == 0), axis=0) 

        clmns = ['x','y','z','red','green','blue']
        pcd_pd = pd.DataFrame(data=pcd_np,columns=clmns)
        pcd_pd['red'] = sigma_value.astype(np.uint8)

        pcd_points = PyntCloud(pcd_pd)
        edge_points = PyntCloud(pd.DataFrame(data=edge_np,columns=clmns))

        PyntCloud.to_file(edge_points, outputPath) # Save just the edge points
