#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 00:46:50 2021

@author: bruzewskis

This is a simple code created to run a 2d world using a slightly updated
encoding scheme that makes things quite a bit faster overall.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import imageio
import multiprocessing as mp
import argparse as ap
from gameengine import Conway

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
    
    if True:
        # Used to return the plot as an image rray
        fig.canvas.draw()       # draw the canvas, cache the renderer
        image = np.array(fig.canvas.buffer_rgba())[:, :, :3]
        
        plt.close(fig)
    
        return image

def save_out_mov(worlds, plot_func, savename, fps=5):
    # Multiprocess the cool stuff
    p = mp.Pool(mp.cpu_count()-1)
    ims = p.map(plot_func, worlds)
    p.close()
    
    # Plot
    if not savename is None:
        kwargs = {'fps':fps, 'quality':9, 'codec':'h264'}
        with imageio.get_writer(savename, **kwargs) as writer:
            for im in ims:
                writer.append_data(im)


if __name__=='__main__':
    
    parser = ap.ArgumentParser()
    parser.add_argument('-N', '--Nsize', help='Size of one dim', type=int, default=5)
    parser.add_argument('-D', '--dim', help='Dimensionality', type=int, default=3)
    parser.add_argument('-P', '--prob', help='Fill probability', type=float, default=0.2)
    parser.add_argument('-R', '--rule', help='Rule', nargs='+', type=int, default=(4,5,5,5))
    args = parser.parse_args()
    
    np.random.seed(69)
    
    rules = [(4,5,5,5),
             (5,7,6,6),
             (5,6,5,5)]
    
    c = Conway(shape = (args.Nsize,)*args.dim,
               prob = args.prob,
               rule = tuple(args.rule))
    
    print(repr(c))
    
    c.run_world(50)
    print('Ran for:', len(c.history))
    worlds = c.history
    write_name = c.get_unique_name() + '.mp4'
    print('Working on:', write_name)
    save_out_mov(worlds, view_world, write_name)
    