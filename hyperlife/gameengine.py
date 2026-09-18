"""
Created on Wed Jun 30 21:18:30 2021.

@author: bruzewskis
"""

from dataclasses import dataclass, field
import numpy as np
from tqdm import trange

__author__ = "Seth Bruzewski"
__credits__ = ["Seth Bruzewski", "Pham Nguyen"]

__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Seth Bruzewski"
__email__ = "bruzewskis@unm.edu"
__status__ = "development"


@dataclass
class Conway:
    """
    An engine class for Life.

    The Conway's Game of Life pythonic engine for running GoL at any
    dimension, size, rule, and initial soupy beginnings. This method
    encodes the world in such a way that any given cell describes both its
    own state and its local neighbourhood.
    """

    shape: tuple = (10, 10)
    prob: float = 0.3
    rule: str | tuple = 'B3/S23'
    seed: int = field(default=None, repr=False)
    world: np.ndarray = field(default=None, repr=False)
    history: list = field(init=False, repr=False)

    def __post_init__(self):
        """
        Post initialize the world using the input/default params.

        Returns
        -------
        None.

        """
        # Parse the rule, either a 'B3/S23' string or an (e_l, e_u, f_l, f_u)
        # tuple of inclusive survive/birth ranges, which is needed once
        # higher dimensions allow neighbour counts above 9
        if isinstance(self.rule, str):
            bstr, sstr = self.rule.split('/')
            self.born_set = set([int(b) for b in bstr[1:]])
            self.surv_set = set([int(s) for s in sstr[1:]])
        else:
            e_l, e_u, f_l, f_u = self.rule
            self.surv_set = set(range(e_l, e_u+1))
            self.born_set = set(range(f_l, f_u+1))

        # Determine how to set up world
        if self.world is None:
            if self.seed is not None:
                np.random.seed(self.seed)

            # Generate a simplistic world
            init_world = np.random.choice(a=[0, 1],
                                          size=self.shape,
                                          p=[1-self.prob, self.prob])

            # Start building the world
            self.world = init_world.copy()

        else:
            # Set up the world provided
            init_world = self.world.copy()
            self.shape = self.world.shape

        # Iterate over all the indices
        for ind, cell in np.ndenumerate(init_world):

            # If we find an alive cell, let the neighbours know
            if cell & 1:
                hind = self.get_hyper_indices(np.array(ind))
                self.world[hind] += 2
                self.world[ind] -= 2

        # Delete this to conserve memory
        del init_world

        # Start keeping track
        self.history = [self.world]

    def __str__(self):
        """
        Generate a string of the current world using some numpy shortcuts.

        Returns
        -------
        world_str : str
            Stirng representation of the world.
        """
        world_str = np.array2string(self.world, threshold=10)
        return world_str

    def get_unique_name(self):
        """
        Generate a unique name from the properties of the object.

        Returns
        -------
        name : str
            A unique name generated from instance variables.

        """
        shape_str = f"n{'x'.join(map(str, self.shape))}_d{len(self.shape)}"
        prob_str = f'p{round(100*self.prob):02d}'
        if isinstance(self.rule, str):
            rule_str = self.rule.replace('/', '')
        else:
            rule_str = 'e{0:02d}_e{1:02d}_f{2:02d}_f{3:02d}'.format(*self.rule)
        name = f'world_{shape_str}_{prob_str}_{rule_str}'

        return name

    def get_hyper_indices(self, coord):
        """
        Helper/utility function which identifies coordinates of neighbours.

        Parameters
        ----------
        coord : np.ndarray
            Coordinate in the world to search around, should be a 1d array of
            length self.dim.

        Returns
        -------
        hind : np.ndarray
            A array of indices which can be easily inserted into the world
            array to extract or modify a subset of the world.

        """
        # Generate offset array
        dind = np.array([[-1, 0, +1]]*self.world.ndim).T

        # Convert to array coordinates
        cind = (dind + coord).T
        cind %= np.array([self.world.shape]).T  # wrap

        # Extract hyper-coordinates
        hind = np.ix_(*cind)

        return hind

    def update_world(self):
        """
        Update the world through a single iteration.

        Returns
        -------
        None.

        """
        new_world = np.copy(self.world)

        # Iterate in space
        for ind, cell in np.ndenumerate(self.world):

            # Skip if dead and no friends
            if cell == 0:
                continue

            # Grab the number of neighbours
            num = cell >> 1

            # Establish that no shift might be needed
            shift = 0

            # Check if it's alive or dead
            if cell & 1:
                # Do we need to kill it?
                if num not in self.surv_set:
                    # Kill the cell
                    new_world[ind] ^= 1
                    shift = -2

            else:
                # Do we need to alive it?
                if num in self.born_set:
                    # Make the cell alive
                    new_world[ind] ^= 1
                    shift = +2

            # Update the neighbours if something happened
            if shift != 0:
                hind = self.get_hyper_indices(ind)
                new_world[hind] += shift
                new_world[ind] -= shift  # correct the original cell

        # Overwrite current world
        self.world = new_world

        # Delete temp one for memory
        del new_world

        # Append to history
        self.history.append(self.world)

        return None

    def run_world(self, iters, progress=False):
        """
        Run the world forward up to some number of iterations.

        Parameters
        ----------
        iters : int
            Number of iterations to progress the world.

        Returns
        -------
        None.

        """
        iterator = trange(iters-1) if progress else range(iters-1)
        # Iterate in time
        for t in iterator:

            self.update_world()

            # End run if the world died early or reached equilibrium
            is_world_dead = np.sum(self.world) == 0
            is_world_stale = np.all(self.world == self.history[-2])
            if is_world_dead or is_world_stale:
                break

def make_life(lifestr, shape):
    return np.array(list(lifestr), dtype=int).reshape(shape)

if __name__ == '__main__':
    
    board = np.zeros((50,50), dtype=int)
    glider = make_life('001101011', (3,3))
    block = make_life('1111', (2,2))
    beacon = make_life('1100110000110011', (4,4))
    board[10:13,10:13] = glider
    board[17:20,10:13] = glider
    board[30:32,10:12] = block
    board[10:14,30:34] = beacon
    board[35:,35:] = np.random.choice([1,0], (15,15), p=[0.2,0.8])
    board[40,10] = 1
    
    
    c = Conway(world=board)
    c.run_world(10, True)
    
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10,10))
    plt.imshow(c.history[6]&1, interpolation='nearest', cmap='gray_r')