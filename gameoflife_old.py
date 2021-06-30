import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import imageio
from tqdm import trange, tqdm
import multiprocessing as mp

def create_world(size, frac=0.1, dim=2):
    
    world = np.random.choice([0,1], [size]*dim, p=[1-frac, frac])
        
    return world

def count_neighbours(world, coord):
    
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

def update_world(world, rule_vector):
    
    # Define the rules
    e_l, e_u, f_l, f_u = rule_vector
    
    new_world = world.copy()
    for ind, val in np.ndenumerate(world):
        
        # How is this cell doing
        is_alive = val==1
        neighbors = count_neighbours(world, np.array(ind))
        
        # Whcih rule do we follow
        new_state = 0
        if is_alive:
            if e_l <= neighbors <= e_u:
                new_state = 1 # maintain life
            else:
                new_state = 0 # death via underpop or overpop
        else:
            if f_l <= neighbors <= f_u:
                new_state = 1 # reproduction
            else:
                new_state = 0 # maintain death
            
        # Update map
        new_world[ind] = new_state
            
    return new_world

def cache_plot_2d(world):

    fig, ax = plt.subplots(figsize=(10,10), dpi=108.8, constrained_layout=True)
    ax.imshow(world, cmap='gray')
    ax.axis('off')

    # Used to return the plot as an image rray
    fig.canvas.draw()       # draw the canvas, cache the renderer
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
    image  = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    
    plt.close(fig)

    return image

def cache_plot_3d(world):
    
    fig = plt.figure(figsize=(10,10), dpi=108.8, constrained_layout=True)
    ax = fig.add_subplot(111,projection='3d')
    ax.voxels(world, edgecolor='k')
    ax.axis('off')

    # Used to return the plot as an image rray
    fig.canvas.draw()       # draw the canvas, cache the renderer
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
    image  = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    
    plt.close(fig)

    return image

def cache_plot_4d_v1(world):
    if len(world)!=9:
        raise ValueError('Need smaller world')
    
    fig = plt.figure(figsize=(16,9), dpi=68)
    ax = plt.subplot2grid((3,6),(0,0), colspan=3, rowspan=3, projection='3d')
    for i in range(len(world)):
        subspace = world[i]
        cn = (1-i/len(world))*255
        color = cm.viridis( int(cn) )
        ax.voxels(subspace, facecolor=color, edgecolor='k', alpha=0.5)
        
        if i%1==0:
            ax2 = plt.subplot2grid((3,6), (i//3, i%3+3), projection='3d')
            ax2.voxels(world[i], facecolor=color, edgecolor='k')
            ax2.axis('off')
    ax.axis('off')
    

    # Used to return the plot as an image array
    fig.canvas.draw()       # draw the canvas, cache the renderer
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
    image  = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    
    plt.close(fig)

    return image

def cache_plot_4d_v2(world):
    
    fig = plt.figure(figsize=(16,9), dpi=68)
    ax = plt.subplot2grid((1,2),(0,0), projection='3d')
    for i in range(len(world)):
        subspace = world[i]
        cn = (1-i/len(world))*255
        color = cm.viridis( int(cn) )
        ax.voxels(subspace, facecolor=color, edgecolor='k', alpha=0.5)
    ax.axis('off')
        
    mid_i = len(world)//2
    mid_c = cm.viridis(int((1-mid_i/len(world))*255))
    ax2 = plt.subplot2grid((1,2), (0,1), projection='3d')
    ax2.voxels(world[mid_i], facecolor=mid_c, edgecolor='k')
    ax2.axis('off')
    plt.tight_layout()
    

    # Used to return the plot as an image array
    fig.canvas.draw()       # draw the canvas, cache the renderer
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
    image  = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    
    plt.close(fig)

    return image

def run_world(world, rule_vector=(2,3,3,3), niter=100):
    
    # Initialize
    worlds = [ world ]
    
    # Update
    for _ in range(niter):
        world = update_world(world, rule_vector)
        worlds.append( world )
        
        # Check for world death
        if np.all(~world.astype(bool)):
            print('Total World Death')
            break
    
    return worlds

def save_out_mov(worlds, plot_func, savename, fps=1):
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
                
    return None
    
if __name__=='__main__':
#    world_2d = create_world(50, frac=0.2, dim=2)
#    final_world = run_world(world_2d, cache_plot_2d, 'gol_2d.mp4')
    
#    world_3d = create_world(15, frac=0.1, dim=3)
#    final_world = run_world(world_3d, cache_plot_3d, 'gol_3d.mp4', 
#                            rule_vector=(4,5,5,5), niter=50)
    
#    world_4d = create_world(9, frac=0.05, dim=4)
    
    
    world = np.zeros([50]*4)
    m = len(world)//2
    world[m, m-5:m+6, m-5:m+6, m-5:m+6] = np.random.choice([0,1], [11]*3, p=[0.9,0.1])
    worlds = run_world(world, rule_vector=(3,5,5,5), niter=1)
                    
    save_out_mov(worlds, cache_plot_4d_v2, 'gol4d_{0:02d}.mp4'.format(0))
    
    # ( EU, EL, FU<27, FL )
    
    