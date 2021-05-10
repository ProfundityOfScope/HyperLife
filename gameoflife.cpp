// Game of Life testing

#include <iostream>
#include <string>
using namespace std;

template< typename T, size_t N, size_t M >
void printArray( T(&theArray)[N][M]  ) {
    for ( int x = 0; x < N; x ++ ) {
    	cout << ((x==0) ? "[[" : " [");
        for ( int y = 0; y < M; y++ ) {
            cout << " " << ((theArray[x][y]) ? "T" : "F") << " ";
        }
        cout << ((x==N-1) ? "]]" : "]") << endl;
    }
}

int main() {
    cout << "Hey look it's a board" << endl;

    const int board_size = 10;
    bool array[board_size][board_size] = {0};
    printArray(array); 
    return 0;
}