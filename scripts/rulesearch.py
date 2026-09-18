#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 00:46:50 2021

@author: bruzewskis

This is a simple code created to run a 2d world using a slightly updated
encoding scheme that makes things quite a bit faster overall.
"""

import numpy as np
# import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LogNorm
import imageio
import multiprocessing as mp
import argparse as ap
from gameengine import Conway
from time import time
import skimage
from io import BytesIO
import sys
from tqdm import trange

def view_world(w):
    '''
    This plotting function has been rigged up so it returns an image object
    that can be encoded into a video file as a frame

    Parameters
    ----------
    w : numpy.ndarray
        World to be drawn.

    Returns
    -------
    image : np.ndarray
        Reformated array which can be written out.

    '''
    
    norm = Normalize(vmin=0, vmax=6)
    colors = plt.cm.viridis(norm(w>>1))
    # colors[:,:,:,3] = 0.8
    
    fig = plt.figure(figsize=(16,9+2/30), dpi=120)
    
    ax1 = plt.subplot2grid((1,2),(0,0), fig=fig, projection='3d')
    ax1.voxels(w&1)
    ax1.axis('off')
    
    ax2 = plt.subplot2grid((1,2),(0,1), fig=fig, projection='3d')
    ax2.voxels(w>>1, facecolors=colors)
    ax2.axis('off')
    
    plt.tight_layout()
    
    if False:
        # Used to return the plot as an image rray
        fig.canvas.draw()       # draw the canvas, cache the renderer
        image = np.array(fig.canvas.buffer_rgba())[:, :, :3]
        
        plt.close(fig)
    
        return image
    return None
    
def view_4d(w):
    
    fig = plt.figure(figsize=(10,10), dpi=120)
    
    stacked = np.sum(w&1, axis=0)
    print(stacked.shape)
    
    
    shadow = np.zeros_like(w[0])
    
    ax = plt.subplot(projection='3d')
    for i in range(len(w)):
        to_set = np.nonzero(w[i]&1)[0]
        shadow[to_set] = i
        
    shadow = np.argmax(w&1, axis=0)
    
    norm = Normalize(vmin=0, vmax=len(w))
    colors = plt.cm.viridis(norm(shadow))
    ax.voxels(shadow, facecolors=colors)
    plt.tight_layout()


def get_compression_ratio(a):

    uncompressed = BytesIO()
    compressed = BytesIO()
    np.savez_compressed(compressed, a)
    np.savez(uncompressed, a)

    return sys.getsizeof(uncompressed)/sys.getsizeof(compressed)

if __name__=='__main__':
    
    
    maxrun = 50
    
    survive_arr = np.arange(4,15)
    fertile_arr = np.arange(5,10)
    shape_for = len(survive_arr), len(fertile_arr)
    
   
    
    rs = np.random.randint(0,1000)
    
    for sgap in range(1,3):
        
        run_length = np.zeros(shape_for)
        run_entr = np.zeros(shape_for)
        run_ends = np.zeros(shape_for)
        run_mean = np.zeros(shape_for)
        run_std = np.zeros(shape_for)
        
        for i in range(len(survive_arr)):
            surv = survive_arr[i]
            for j in trange(len(fertile_arr)):
                fert = fertile_arr[j]
                
                test_rule = surv, surv+sgap, fert, fert
                # c = Conway(rule = test_rule, world=test_world.copy())
                c = Conway((20,)*4, 0.2, test_rule, seed=rs)
                
                
                c.run_world(maxrun)
                worlds = c.history
                
                count = np.array([ np.sum(w&1) for w in worlds ])
                se = [ get_compression_ratio(w) for w in worlds]
                
                run_length[i][j] = len(count)
                run_entr[i][j] = se[-1]/se[0]
                run_ends[i][j] = count[-1]/count[0]
                run_mean[i][j] = np.mean(count)/count[0]
                run_std[i][j] = np.std(count)/count[0]
              
        ims = [run_entr, run_mean, run_ends, run_std]
        name = ['compressability', 'mean factor', 'end factor', 'variance']
        spot = [ (0,0), (0,1), (1,0), (1,1)]
        dies_early = run_length != maxrun
        
        fig = plt.figure(figsize=(8,8))
        for i in range(4):
            
            ee = [min(fertile_arr)-0.5, max(fertile_arr)+0.5, 
                  min(survive_arr)-0.5, max(survive_arr)+0.5]
            im = ims[i]
            im[dies_early] = np.nan
            
            plt.subplot2grid((2,2), (i//2, i%2))
            plt.imshow(im, origin='lower', extent=ee, norm=LogNorm())
            plt.title(f'{name[i]} (sg={sgap})')
            plt.xlabel('fertile')
            plt.xticks(np.arange(np.min(fertile_arr),np.max(fertile_arr)+1))
            plt.ylabel('survive')
            plt.yticks(np.arange(np.min(survive_arr),np.max(survive_arr)+1))
            plt.colorbar()
        break
    
    
    