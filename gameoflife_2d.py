#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 00:46:50 2021

@author: bruzewskis

This is a simple code created to run a 2d world using a slightly updated
encoding scheme that makes things quite a bit faster overall.
"""

import numpy as np
import matplotlib.pyplot as plt
import imageio

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
    
    fig = plt.figure(figsize=(16,9+2/30), dpi=120)
    
    ax1 = plt.subplot2grid((1,2),(0,0), fig=fig)
    ax1.imshow(w&1, cmap='Greys_r')
    ax1.axis('off')
    
    ax2 = plt.subplot2grid((1,2),(0,1), fig=fig)
    ax2.imshow(w>>1, vmin=0, vmax=8)
    ax2.axis('off')
    
    plt.tight_layout()

    # Used to return the plot as an image rray
    fig.canvas.draw()       # draw the canvas, cache the renderer
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
    image  = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    
    plt.close(fig)

    return image


def create_world(n, p=0.1):
    '''
    This function does what you'd expect, it just makes a world

    Parameters
    ----------
    n : int
        The size of the world, keeping in mind that the generated 2d world 
        will be an nxn square.
    p : float, optional
        Probability for a cell to begin as alive, between 0 and 1. The
        probability to begin as dead is then 1-p. The default is 0.1.

    Returns
    -------
    world : numpy.ndarray
        The generated world matching the input parameters.

    '''
    world = np.random.choice(np.array([0,1],dtype=int), (n,n), p=[1-p, p])
    return world

def count_neighbours(world, coord):
    '''
    A helper function that uses numpy hyperslicing to very quickly count the
    number of neighbours a cell has.

    Parameters
    ----------
    world : numpy.ndarray
        The world which will be searched.
    coord : numpy.ndarray
        An array containing the target indices to search around. This function
        was generalized for higher dimensional arrays, so for a 2d case, the
        input is expected as e.g. np.array([i,j]).

    Returns
    -------
    num_neighbours : int
        The number of neighbours found in the nearby cells.

    '''
    
    # Generate offset array
    dind = np.array([[-1,0,1]]*world.ndim)
    
    # Convert to array coordinates
    cind = (dind.T + coord).T
    
    # Wrap edges
    cind %= np.array([world.shape]).T
    
    # Extract neighbours
    neighbors = world[np.ix_(*cind)]
    
    # Count alive in neighbourhood, subtract queried point if alive
    num_neighbours = np.sum(neighbors) - world[tuple(coord)]
    
    return num_neighbours

def encode_world(w):
    '''
    This takes a simplistically generated world and encodes the number of 
    neighbours each cell has into the cells state, allowing for us to use
    the encoded cell algorithm for a dramatic speedup

    Parameters
    ----------
    w : numpy.ndarray
        World which will be encoded.

    Returns
    -------
    n : numpy.ndarray
        World which has been encoded.

    '''
    
    n = np.zeros_like(w)
    
    for i in range(len(w)):
        for j in range(len(w[i])):
            # Grab number of neighbours
            neighbours = count_neighbours(w, np.array([i, j]))
            # The first (leftmost) bit encodes the alive/dead state
            # The other bits encode the number of neighbours
            n[i,j] = neighbours << 1 | w[i,j]
    
    return n

def run_eworld(w, t):
    '''
    This runs an encoded world using the sped up algorithm.

    Parameters
    ----------
    w : numpy.ndarray
        The encoded world which will be run forward.
    t : int
        How many iterations to run the world forward, at maximum.

    Returns
    -------
    n : list<numpy.ndarray>
        A list containing the iterated worlds. n[0] will be the input world w, 
        and n[-1] will either be the world after t iterations, or after all
        the world has died off.

    '''
    # Initialize tracking
    n = [w]
    
    # Useful for modulos
    width = len(w)
    
    # Iterate in time
    for k in range(1,t):
        
        c = np.copy(n[k-1])
        
        # Iterate in space
        for i in range(len(w)):
            for j in range(len(w[i])):
                
                # Get encoded value of cell
                cell = n[k-1][i][j]
                
                # Skip if dead and no friends
                if cell == 0:
                    continue
                
                # Grab the number of neighbours
                num = cell >> 1
                
                # Check if it's alive or dead
                if cell&1:
                    
                    # Do we need to kill it?
                    if not (1<num<4):
                        # Kill the cell
                        c[i][j] ^= 1
                        
                        # Update the neighbours
                        for x in range(-1, 2):
                            for y in range(-1,2):
                                # Skip cell itself
                                if x==0 and y==0:
                                    continue
                                # Tell neighbours it's dead
                                c[(i+x)%width][(j+y)%width] -= 2
                                
                else:
                    
                    # Do we need to alive it?
                    if num==3:
                        # Make the cell alive
                        c[i][j] ^= 1
                        
                        # Update the neighbours
                        for x in range(-1, 2):
                            for y in range(-1,2):
                                # Skip cell itself
                                if x==0 and y==0:
                                    continue
                                # Tell neighbours it's alive
                                c[(i+x)%width][(j+y)%width] += 2
                                
        n.append(c)
        
        # Let the user know if the world died early
        if np.sum(c)==0:
            print('EARLY WORLD TERMINATION')
            break
        
    return n


if __name__=='__main__':
    
    world = create_world(100, 0.5)
    eworld = encode_world(world)
    
    tmax = 100
        
    start = time()
    run_worlds = run_eworld(eworld, tmax)
    total = time() - start
    print('Took', total, 'seconds')
        
    kwargs = {'fps':5, 'quality':9, 'codec':'h264'}
    with imageio.get_writer('encodedworld.mp4', **kwargs) as writer:
        for rworld in run_worlds:
            im = view_world(rworld)
            writer.append_data(im)
    