// Game of Life testing

#include <iostream>
#include <string>
using namespace std;

typedef unsigned char board;

void printboard_old( board *board, const unsigned int shape[2]  ) {
    for ( int i = 0; i < shape[0]; i++ ) {
        for ( int j = 0; j < shape[1]; j++ ) {
        	int offset = i*shape[0] + j;
            cout << dec << *(board + i*shape[0] + j) << " ";
        }
        cout << endl;
    }
}

void updateWorld( board *&board1, board *&board2, const unsigned int shape[2] ) {
	for ( int i = 0; i < shape[0]; i++ ) {
        for ( int j = 0; j < shape[1]; j++ ) {

        	// For ease of access
        	unsigned char cell = *(board1 + i*shape[0] + j);

        	// Skip Empty Cells
        	if ( cell == 0 ) {
        		continue;
        	}

        	// Get these to make life easier
        	bool is_alive = cell & 1;
        	int num_neighbours = cell >> 1;

        	if (is_alive && !(num_neighbours==2 || num_neighbours==3)) {
        		cout << cell << "This cell needs to die\n";
				// Update board2/old_board
        		// Set cell to dead
        		// Subtract 1 from neighbour_counts of nearby cells
        	}
        	else if (!is_alive && num_neighbours==3) {
        		cout << cell << "This cell is to be reborn\n";
        		// Update board2/old_board
        		// Set cell to alive
        		// Add 1 from neighbour_counts of nearby cells
        	}
        }
    }

    // Swap the pointers!
    swap(board1, board2);
}

int main() {

	// Set up boards
    const unsigned int board_shape[2] = {10,10};
    board board_old[100] = {0b0};
    board board_new[100];

    // Board pointers
    board *bptr_old = board_old;
    board *bptr_new = board_new;

    // Initialize an oscillator
    board_old[54] = 0x03;
    board_old[55] = 0x05;
    board_old[56] = 0x03;

    // Oscillator's neighbours
    board_old[43] = board_old[63] = 0x02;
    board_old[44] = board_old[64] = 0x04;
    board_old[45] = board_old[65] = 0x06;
    board_old[46] = board_old[66] = 0x04;
    board_old[47] = board_old[67] = 0x02;

    // Initialize one lonely cell
    board_old[22] = 0x01;

    // Lonely cell's neighbours
    board_old[11] = board_old[12] = board_old[13] = 0x02;
    board_old[21] = board_old[23] = 0x02;
    board_old[31] = board_old[32] = board_old[33] = 0x02;

    // Copy over data to new
    copy(begin(board_old), end(board_old), begin(board_new));

    // This is basically the bit that goes in the loop
    printboard_old(bptr_new, board_shape);
    updateWorld(bptr_new, bptr_old, board_shape);
    // Probably dump board to file at this point
    // Loop back
    
    return 0;
}