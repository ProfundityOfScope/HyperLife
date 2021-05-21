// Game of Life testing

#include <iostream>
#include <string>
using namespace std;

typedef unsigned char board;

void printboard( board *board, const unsigned int shape[2]  ) {
    for ( int i = 0; i < shape[0]; i++ ) {
        for ( int j = 0; j < shape[1]; j++ ) {
        	int offset = i*shape[0] + j;
            cout << (*(board + offset)|0) << " ";
        }
        cout << endl;
    }
}

int mod(int a, int b) {
    // This function literally just emulates how python does modulo
    // -2%10 = 8 deal with it
    int c = ((a % b) + b) % b;
    return c;
}

void updateNeighbors( board *&board, const unsigned int shape[2], 
    unsigned long long offset, short value) {

    // Here we need to jump around the array and add value (+2/-2)
    int o_r = offset/shape[0];
    int o_c = offset%shape[0];

    for ( int i = -1; i < 2; i++ ) {

        // Check the new row for border wrapping
        int n_r = mod((o_r+i), shape[0]);

        for ( int j = -1; j < 2; j++ ) {

            // Check the new col for border wrapping
            int n_c = mod((o_c+j), shape[1]);
            if (i==0 && j==0) {
                continue;
            }

            // Where the heck is this cell really
            unsigned long long n_offset = n_r*shape[0] + n_c;
            *(board + n_offset) += value;
        }
    }
}

void updateWorld( board *&board1, board *&board2, 
    const unsigned int shape[2] ) {
	for ( int i = 0; i < shape[0]; i++ ) {
        for ( int j = 0; j < shape[1]; j++ ) {

        	// For ease of access
            unsigned long long offset = i*shape[0] + j;
        	unsigned char* cell_ptr = board1 + offset;
            unsigned char cell_val = *cell_ptr;
        	// Skip Empty Cell
        	if ( cell_val == 0 ) {
        		continue;
        	}

        	// Get these to make life easier
        	bool is_alive = cell_val & 1;
        	int num_neighbours = cell_val >> 1;

        	if (is_alive && !(num_neighbours==2 || num_neighbours==3)) {
        		// Set cell to dead
                *(board2 + offset) -= 1;
                // Subtract 1 from neighbour_counts of nearby cells
                updateNeighbors(board2, shape, offset, -2);
        	}
        	else if (!is_alive && num_neighbours==3) {
        		// Set cell to alive
                *(board2 + offset) += 1;
                // Add 1 from neighbour_counts of nearby cells
                updateNeighbors(board2, shape, offset, +2);
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
    board_old[43] = board_old[53] = board_old[63] = 0x02;
    board_old[44] = board_old[64] = 0x04;
    board_old[45] = board_old[65] = 0x06;
    board_old[46] = board_old[66] = 0x04;
    board_old[47] = board_old[57] = board_old[67] = 0x02;

    // Initialize one lonely cell
    board_old[22] = 0x01;

    // Lonely cell's neighbours
    board_old[11] = board_old[12] = board_old[13] = 0x02;
    board_old[21] = board_old[23] = 0x02;
    board_old[31] = board_old[32] = board_old[33] = 0x02;

    // Copy over data to new
    copy(begin(board_old), end(board_old), begin(board_new));

    // This is basically the bit that goes in the loop
    printboard(bptr_new, board_shape);

    for (int i = 0; i<5; i++) {
        updateWorld(bptr_new, bptr_old, board_shape);
        cout << "\n";
        printboard(bptr_new, board_shape);
    }
    // Probably dump board to file at this point
    // Loop back
    
    return 0;
}