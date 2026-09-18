#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  4 22:31:47 2023

@author: bruzewskis
"""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from scipy import ndimage
from gameengine import Conway

def state_function(x):
    return np.piecewise(x, [x==2, x==3], [0, 1, -1])

def update_color_world(w):
    kernel = np.stack((np.array([[1,1,1],[1,0,1],[1,1,1]])*-0.5,
                       np.array([[1,1,1],[1,0,1],[1,1,1]]),
                       np.array([[1,1,1],[1,0,1],[1,1,1]])*0.5), axis=-1) # R G B
    neighbours = ndimage.convolve(w, kernel, mode='wrap')
    delta = state_function(neighbours)
    new_world = np.clip(w + delta, 0, 1)
    return new_world


n = 300
p = 0.1
steps = 150
fps = 10
world = np.random.choice((1, 0), (n, n, 3), p=(p, 1-p))

history = np.zeros((steps, n, n, 3), dtype=np.float32)
for i in range(steps):
    history[i] = world
    world = update_color_world(world)


fig = plt.figure(figsize=(5, 5), dpi=1920/5, layout='constrained')
ax = fig.add_subplot()
im = ax.imshow(1-history[steps-1], interpolation='none', rasterized=True)
plt.axis('off')
plt.savefig('thumb.png', bbox_inches='tight')

def update(frame):
    im.set_data(1-history[frame])
    return im,


ani = FuncAnimation(fig, update, frames=steps, interval=1000/fps, blit=True)
ani.save('channels.mp4', writer='ffmpeg')
plt.show()

alive = np.sum(history, axis=(1,2,3)) / (n*n*3)
# plt.plot(alive/(n*n*3))
# plt.ylim(0,1)