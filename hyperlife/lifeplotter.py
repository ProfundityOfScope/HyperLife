#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 23:53:12 2021

@author: bruzewskis
"""

import numpy as np
# import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LogNorm
import imageio
from gameengine import Conway

def view_2d(w, return_draw=False, view=(None,None)):
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
    
    fig = plt.figure(figsize=(16,9+2/30), dpi=120)
    
    ax1 = plt.subplot2grid((1,1),(0,0), fig=fig)
    ax1.imshow(w&1, cmap='Greys_r')
    ax1.axis('off')
    
    plt.tight_layout()
    
    if return_draw:
        # Used to return the plot as an image array
        fig.canvas.draw()       # draw the canvas, cache the renderer
        image = np.array(fig.canvas.buffer_rgba())[:, :, :3]
        plt.close(fig)
    
        return image
    else:
        plt.show()
        
        return None

def view_3d(w, return_draw=False, view=(None,None), aura=False):
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
    
    fig = plt.figure(figsize=(16,9+2/30), dpi=120)
    
    ax = plt.subplot(projection='3d')
    if aura:
        colors[:,:,:,3] = 0.3
        ax.voxels(w>>1, facecolors=colors)
        
    ax.voxels(w&1, facecolors='w', edgecolors='k')
    ax.axis('off')
    ax.view_init(*view)
    
    plt.tight_layout()
    
    if return_draw:
        # Used to return the plot as an image array
        fig.canvas.draw()       # draw the canvas, cache the renderer
        image = np.array(fig.canvas.buffer_rgba())[:, :, :3]
        plt.close(fig)
    
        return image
    else:
        plt.show()
        
        return None

def view_4d(w, return_draw=False, view=(None,None)):
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
    
        
    shadow = np.argmax(w&1, axis=0)
    norm = Normalize(vmin=0, vmax=len(w))
    colors = plt.cm.viridis(norm(shadow))
    
    fig = plt.figure(figsize=(16,9+2/30), dpi=120)
    
    ax = plt.subplot(projection='3d')
    ax.voxels(shadow, facecolors=colors)
    plt.tight_layout()
    ax.view_init(*view)
    # plt.axis('off')
    
    if return_draw:
        # Used to return the plot as an image array
        fig.canvas.draw()       # draw the canvas, cache the renderer
        image = np.array(fig.canvas.buffer_rgba())[:, :, :3]
        plt.close(fig)
    
        return image
    else:
        plt.show()
        
        return None



def view_world(w, return_draw=False, **kwargs):
    
    if w.ndim == 2:
        drawing = view_2d(w, return_draw, **kwargs)
    elif w.ndim == 3:
        drawing = view_3d(w, return_draw, **kwargs)
    elif w.ndim == 4:
        drawing = view_4d(w, return_draw, **kwargs)
    else:
        print("I have no idea what this is")
        drawing = None
        
    return drawing

def write_history(history, savename, fps=5):
    if not savename is None:
        kwargs = {'fps':fps, 'quality':9, 'codec':'h264'}
        with imageio.get_writer(savename, **kwargs) as writer:
            for world in history:
                im = view_world(world, True)
                writer.append_data(im)

if __name__=='__main__':
    # c = Conway((20,)*4, 0.2, rule=(5,6,8,8))
    # c.run_world(30)
    # view_world(c.world)
    
    # for i in range(len(c.history)):
    #     view_world(c.history[i])
    
    p = 1e-2
    w = np.random.choice(np.array([0,1], dtype=int), tuple([10]*3), p=[1-p,p])
    c = Conway((100, 100), 0.1, (2,3,3,3))
    print('Running')
    c.run_world(100)
    w = c.world
    print('Drawing')
    view_world(w)
    write_history(c.history, 'simple2dtest.mp4')