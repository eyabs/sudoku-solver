#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

import numpy as np

class Coordinates:
    def __init__(self, row = 0, col = 0):
        self.row = row
        self.col = col
    def __str__(self):
        return '<{0}, {1}>'.format(self.row, self.col)

class SudokuGrid:
    k_GRID_SIZE = 9
    k_BOX_SIZE = 3
    k_VALID_NUMBERS = np.arange(k_GRID_SIZE) + 1 # One thru nine in an numpy array.

    def __init__(self, grid_array = None):
        self.init_grid()
        if (grid_array is not None):
            self.grid = grid_array.copy()
         
        self.is_solved = False
    
    def to_string(self):
        return_string = ''
        
        for row in range(self.k_GRID_SIZE):
            for col in range(self.k_GRID_SIZE):
                return_string = return_string + str(self.grid[row, col]) +  ' '
                if ((col + 1) % self.k_BOX_SIZE == 0):
                    return_string = return_string + ' '
            return_string = return_string + '\n'
            if ((row+1) % self.k_BOX_SIZE == 0):
                return_string = return_string + '\n'
        #    return_string = return_string + ' '.join(str(x) for x in self.grid[row]) + '\n'
        #return_string = 
        return return_string
                       
    def __str__(self):
        return self.to_string()
    
    def copy(self):
        new_grid = self.grid.copy()
        new_candidates = self.candidates.copy()
        new_sudoku_grid = SudokuGrid(new_grid)
        new_sudoku_grid.candidates = self.candidates
        return new_sudoku_grid

    # Initialize each row and column to have all possiblities.
    def init_grid(self):
        self.grid = np.zeros( (self.k_GRID_SIZE, self.k_GRID_SIZE) , dtype = 'int8')
        self.candidates = np.zeros( (self.k_GRID_SIZE, self.k_GRID_SIZE, self.k_GRID_SIZE), dtype = 'int8')
        for row in range(self.k_GRID_SIZE):
            for col in range(self.k_GRID_SIZE):
                self.candidates[row][col] = self.k_VALID_NUMBERS

    def set_grid_from_prompt(self):
        temp_grid = np.zeros( (self.k_GRID_SIZE, self.k_GRID_SIZE) , dtype = 'int8')
        print 'Enter each row with space separated numbers, and with 0 for unkown boxes.'
        for row in range(self.k_GRID_SIZE):
            row_string = raw_input('row {0}\t--> '.format(row + 1))
            row_arr = np.array(row_string.split(' '))

            for col in range(self.k_GRID_SIZE):
                self.grid[row] = int(row_arr[col])
    def get_row_coords(self, coordinate):
        return_arr = np.array([], dtype='object')
        row = coordinate.row
        col = coordinate.col
        for loop_col in range(self.k_GRID_SIZE):
            if (loop_col != col):
                coord = Coordinates(row, loop_col)
                return_arr = np.append(return_arr, coord)

        return return_arr

    def get_col_coords(self, coordinate):
        return_arr = np.array([], dtype='object')
        row = coordinate.row
        col = coordinate.col
        for loop_row in range(self.k_GRID_SIZE):
            if (loop_row != row):
                coord = Coordinates(loop_row, col)
                return_arr = np.append(return_arr, coord)

        return return_arr

    def get_box_coords(self, coordinate):
        return_arr = np.array([], dtype='object')
        row = coordinate.row
        col = coordinate.col
        row_in_box  = row % self.k_BOX_SIZE
        col_in_box  = col % self.k_BOX_SIZE
        row_offsets = range( -1 * (row_in_box), (self.k_BOX_SIZE - row_in_box)) 
        col_offsets = range( -1 * (col_in_box), (self.k_BOX_SIZE - col_in_box))
        for r in row_offsets:
            for c in col_offsets:
                coord = Coordinates(row + r, col + c)
                return_arr = np.append(return_arr, coord)
        return return_arr
    
    def get_row_numbers(self, row, col):
        value = self.grid[row, col]
        numbers = self.grid[row, :].copy()
        return numbers[numbers != value]

    def get_col_numbers(self, row, col):
        value = self.grid[row, col]
        numbers = self.grid[:, col].copy()
        return numbers[numbers != value]

    def get_box_numbers(self, row, col):
        return_arr = np.array([], dtype = 'int8')

        ## Replaced logic with get_box_coords function
        # row_in_box  = row % self.k_BOX_SIZE
        # col_in_box  = col % self.k_BOX_SIZE
        # row_offsets = range( -1 * (row_in_box), (self.k_BOX_SIZE - row_in_box)) 
        # col_offsets = range( -1 * (col_in_box), (self.k_BOX_SIZE - col_in_box))
        # for y in row_offsets:
        #     for x in col_offsets:
        #         if (not((y == row) & (x == col))):
        #             return_arr = np.append(return_arr, int(self.grid[row + y][col + x]))

        coords = self.get_box_coords(Coordinates(row, col))
        for coord in coords:
            r = coord.row
            c = coord.col
            if (not((r == row) & (c == col))):
                return_arr = np.append(return_arr, self.grid[r, c])

        return return_arr

    def value_is_taken(self, row, col, value):
        r = value in self.get_row_numbers(row, col)
        c = value in self.get_col_numbers(row, col)
        b = value in self.get_box_numbers(row, col)
        return ( r
               | c
               | b
               )




class SudokuSolver():
    k_EMPTY_CELL = 0
    # Initialize with optional Sudoku Grid Object param.
    def __init__(self, _sudoku_grid = None):
        if (_sudoku_grid is None):
            self.sudoku_grid = SudokuGrid()
        else:
            self.sudoku_grid = SudokuGrid(_sudoku_grid.grid.copy())
        self.grid_size = _sudoku_grid.k_GRID_SIZE

    def get_grid(self):
        return self.sudoku_grid.grid

    def advance_taken_number(self, row, col, start_number = 1):
        number = start_number
        while (self.sudoku_grid.value_is_taken(row, col, number)):
            number = number + 1
        
        return number

    # Advances the cursor to the next cell, or the first cell in
    # the next row if at the last cell in the row.
    def next_cell(self, coords):
        new_coords = Coordinates()
        new_coords.row = coords.row
        new_coords.col = coords.col

        if (new_coords.col < self.grid_size - 1):
            new_coords.col = new_coords.col + 1
        else:
            new_coords.row = new_coords.row + 1
            new_coords.col = 0
        return new_coords

    def prev_cell(self, coords):
        new_coords = Coordinates()
        new_coords.row = coords.row
        new_coords.col = coords.col

        if (new_coords.col <= 0):
            new_coords.col = self.grid_size - 1
            new_coords.row = new_coords.row - 1
        else:
            new_coords.col = new_coords.col - 1
        return new_coords
        
    def remove_candidate(self, value, coordinate):
        r = coordinate.row
        c = coordinate.col

        mask = (self.sudoku_grid.candidates[r, c, :] == value)
        self.sudoku_grid.candidates[r, c, mask] = 0
    def remove_candidates(self, value, coordinate, region = 'all'):
        coords = np.array([], dtype='object')
        if (str(region).lower() == 'row'):
            coords = self.sudoku_grid.get_row_coords(coordinate)
        elif (str(region).lower() == 'col'):
            coords = self.sudoku_grid.get_col_coords(coordinate)
        elif (str(region).lower() == 'box'):
            coords = self.sudoku_grid.get_box_coords(coordinate)
        elif (str(region).lower() == 'all'):

            row_coords = self.sudoku_grid.get_row_coords(coordinate)
            col_coords = self.sudoku_grid.get_col_coords(coordinate)
            box_coords = self.sudoku_grid.get_box_coords(coordinate)
            coords = np.append(coords, row_coords)
            coords = np.append(coords, col_coords)
            coords = np.append(coords, box_coords)
            coords = np.unique(coords)
        else:  
            raise Exception('Invalid Region:\'' + str(region) + '\'.')
        
        for coord in coords:
            row = coord.row
            col = coord.col
            candidate_mask = (self.sudoku_grid.candidates[row, col] == value)
            self.sudoku_grid.candidates[row, col, candidate_mask] = 0
    
    # update_all_candidates(self)
    # does a single pass through of the sudoku grid removing
    # a number from the candidates list if it exists in the 
    # cells' row, col, or box
    def update_all_candidates(self):
        for row in range(self.sudoku_grid.k_GRID_SIZE):
            for col in range(self.sudoku_grid.k_GRID_SIZE):
                # Known cells' only candidates are themselves.
                coord = Coordinates(row, col)
                cell_value = self.sudoku_grid.grid[row, col]
                if (cell_value != self.k_EMPTY_CELL):
                    known_cell_mask = (self.sudoku_grid.candidates[row, col] != cell_value)
                    #unknown_cell_mask = np.invert(known_cell_mask)
                    self.sudoku_grid.candidates[row, col, known_cell_mask] = 0
                    # Remove this value from candidates in the row, col and box.
                    self.remove_candidates(cell_value, coord, region='all')
                #else:
                    # # Loop over non zero values in the cell's row and remove them from the candidate list.
                    # row_mask = (self.sudoku_grid.grid[row] != 0)
                    # for val in self.sudoku_grid.grid[row_mask]:
                    #     self.remove_candidate(val, coord)

                    # # Loop over non zero values in the cell's col and remove them from the candidate list.
                    # col_mask = (self.sudoku_grid.grid[:,col] != 0)
                    # for val in self.sudoku_grid.grid[:, col_mask]:
                    #     self.remove_candidate(val, coord)

                    # # Loop over non zero values in the cell's col and remove them from the candidate list.
                    # box_numbers = self.sudoku_grid.get_box_numbers(row, col)
                    # box_mask = (box_numbers != 0)
                    # #box_coords = sudoku_grid.get_box_coords(row, col)
                    # for val in box_numbers[box_mask]:
                    #     self.remove_candidate(val, coord)
    
    def pick_single_candidates(self):
        # If a cell only has one candidate, that is the correct number.
        for row in range(self.sudoku_grid.k_GRID_SIZE):
            for col in range(self.sudoku_grid.k_GRID_SIZE):
                candidates = self.sudoku_grid.candidates[row, col]
                if (candidates[candidates != 0].size == 1):
                    val = int(candidates[candidates != 0])
                    self.sudoku_grid.grid[row, col] = val
        self.update_all_candidates()
    
    def pick_lonely_candidates(self):
        # If a cell is the only cell in a row, box, or col with a specific candidate,
        # that is the correct number.
        
        # Check each row for lonely candidates.
        for row in range(self.sudoku_grid.k_GRID_SIZE):
            row_candidates = self.sudoku_grid.candidates[row,:,:]
            for col in range(self.sudoku_grid.k_GRID_SIZE):
                if (self.sudoku_grid.grid[row, col] != 0): continue # Known cell, we can skip it.
                candidates_mask = (row_candidates[col,:] != 0)
                cell_candidates = row_candidates[col,candidates_mask].copy()
                for candidate in cell_candidates:
                    if (row_candidates[row_candidates == candidate].size == 1):
                        # We've found a lonely candidate!
                        self.sudoku_grid.grid[row, col] = candidate
        
        # Check each col for lonely candidates.
        for col in range(self.sudoku_grid.k_GRID_SIZE):
            col_candidates = self.sudoku_grid.candidates[:,col,:]
            for row in range(self.sudoku_grid.k_GRID_SIZE):
                if (self.sudoku_grid.grid[row, col] != 0): continue # Known cell, we can skip it.
                candidates_mask = (col_candidates[row,:] != 0)
                cell_candidates = col_candidates[row, candidates_mask].copy()
                for candidate in cell_candidates:
                    if (col_candidates[col_candidates == candidate].size == 1):
                        # We've found a lonely candidate!
                        self.sudoku_grid.grid[row, col] = candidate

        # Check each box for lonely candidates.
        for box_row in range(0,self.sudoku_grid.k_GRID_SIZE, self.sudoku_grid.k_BOX_SIZE):
            for box_col in range(0,self.sudoku_grid.k_GRID_SIZE, self.sudoku_grid.k_BOX_SIZE):
                # We're looping over the first cells in each box, then getting the other coords from there.
                coords = self.sudoku_grid.get_box_coords(Coordinates(box_row, box_col))
                box_candidates = np.zeros((self.sudoku_grid.k_GRID_SIZE, self.sudoku_grid.k_GRID_SIZE))
                index = 0
                # get the candidates in a more friendly format.
                for coord in coords:
                    row = coord.row
                    col = coord.col
                    box_candidates[index] = self.sudoku_grid.candidates[row, col]
                    index = index + 1
                index = 0
                for coord in coords:
                    row = coord.row
                    col = coord.col
                    if (self.sudoku_grid.grid[row, col] != 0): continue # Known cell, we can skip it.
                    candidates_mask = (box_candidates[index,:] != 0)
                    cell_candidates = box_candidates[index, candidates_mask].copy()
                    for candidate in cell_candidates:
                        if (box_candidates[box_candidates == candidate].size == 1):
                            # We've found a lonely candidate!
                            self.sudoku_grid.grid[row, col] = candidate
                    index = index + 1
        self.update_all_candidates()


    def pick_numbers(self):
        self.pick_single_candidates()
        self.pick_lonely_candidates()


    def simplify_grid(self):
        is_simplified = False
        self.update_all_candidates()
        while(not is_simplified):
            grid_copy = self.sudoku_grid.grid.copy()
            self.pick_numbers()
            
            is_simplified = np.array_equal(grid_copy, self.sudoku_grid.grid)

    def brute_force_solve(self):
        self.grid_copy = self.sudoku_grid.copy()

        index = Coordinates(row = 0, col = 0) 
        test_value = 1
        backtracking = False

        count = 0
        while (index.row < self.grid_size):
            count = count + 1
            if ((index.row < 0) | (index.col < 0)):
                print 'Error!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
                print "r: {0} c: {1} v: {2}".format(index.row, index.col, test_value)
                print self.sudoku_grid.to_string()
                break
            if (count % 10000 == 0):
                #print 'backtracking: '+str(backtracking)+' test_value: ' + str(test_value)
                print str(count) + ': ' + 'row: ' + str(index.row) + ' col: ' + str(index.col) + '\n'
                print self.sudoku_grid.to_string()
                print '\n'
            # if ((count > 649) & (count < 700)):
            #     print 'backtracking: '+str(backtracking)+' test_value: ' + str(test_value)
            #     print str(count) + ': ' + 'row: ' + str(index.row) + ' col: ' + str(index.col) + '\n'
            #     print self.sudoku_grid.to_string()
            #     print '\n'
            if (count > 100000000):
                print self.sudoku_grid.to_string()
                break
            #print ('Backtracking: {0}'.format(backtracking))
            if (not backtracking):
                if (self.grid_copy.grid[index.row][index.col] == self.k_EMPTY_CELL):
                    test_value = self.advance_taken_number(index.row, index.col, start_number = test_value)
                    if (test_value > self.grid_size):
                        # We've picked an invalid value, so we have to go back.
                        self.sudoku_grid.grid[index.row][index.col] = 0
                        backtracking = True
                        #continue
                    else:
                        # Assign the test value to the cell then advance the row/col.
                        self.sudoku_grid.grid[index.row][index.col] = test_value
                        index = self.next_cell(index)
                        backtracking = False
                        test_value = 1
                else:
                    # Cell is a given cell, go to next cell.
                    index = self.next_cell(index)
                    backtracking = False
                    test_value = 1
            else:
                # Backtrack to previous unknown cell.
                #print "r: {0} c: {1} v: {2}".format(index.row, index.col, test_value)
                #self.sudoku_grid.grid[index.row][index.col] = 0
                
                index = self.prev_cell(index)
                while(self.grid_copy.grid[index.row][index.col] != self.k_EMPTY_CELL):
                    index = self.prev_cell(index)
                
                test_value = self.sudoku_grid.grid[index.row][index.col] + 1
                test_value = self.advance_taken_number(index.row, index.col, start_number = test_value)
                if (test_value > self.grid_size):
                    self.sudoku_grid.grid[index.row][index.col] = 0
                    backtracking = True
                else:
                    self.sudoku_grid.grid[index.row][index.col] = test_value
                    index = self.next_cell(index)
                    backtracking = False
                    test_value = 1
        print count



        #for row in range(9):
        #   for col in range(9):
        #       if (self.grid_copy[row][col] == k_EMPTY_CELL):
        #
        #       else:
        #           continue
## ------------------------------------------------------------------------------------------->>
def main():
    
    # test_grid = np.array(
    #   [[11, 12, 13, 14, 15, 16, 17, 18, 19]
    #   ,[21,22,23,24,25,26,27,28,29]
    #   ,[31,32,33,34,35,36,37,38,39]
    #   ,[41,42,43,44,45,46,47,48,49]
    #   ,[51,52,53,54,55,56,57,58,59]
    #   ,[61,62,63,64,65,66,67,68,69]
    #   ,[71,72,73,74,75,76,77,78,79]
    #   ,[81,82,63,84,85,86,87,88,89]
    #   ,[91,92,93,94,95,96,97,98,99]
    #   ])
    
    # test_grid = np.array(
    #     [[5,3,0, 0,7,0, 0,0,0]
    #     ,[6,0,0, 1,9,5, 0,0,0]
    #     ,[0,9,8, 0,0,0, 0,6,0]
    #     ,[8,0,0, 0,6,0, 0,0,3]
    #     ,[4,0,0, 8,0,3, 0,0,1]
    #     ,[7,0,0, 0,2,0, 0,0,6]
    #     ,[0,6,0, 0,0,0, 2,8,0]
    #     ,[0,0,0, 4,1,9, 0,0,5]
    #     ,[0,0,0, 0,8,0, 0,7,9]
    #     ])
    
    # http://kjell.haxx.se/sudoku/ 
    # 179082027-v3-17-L5
    test_grid = np.array(
    [[5,7,0, 0,0,4, 0,8,0]
    ,[0,2,0, 0,0,0, 0,0,0]
    ,[0,0,1, 0,0,0, 0,0,0]

    ,[0,0,3, 5,1,0, 0,0,0]
    ,[0,0,0, 2,0,0, 0,0,0]
    ,[4,0,0, 0,0,0, 0,9,0]

    ,[0,9,0, 0,0,0, 5,4,0]
    ,[0,0,0, 0,7,0, 2,0,0]
    ,[8,0,0, 6,0,0, 0,0,0]
    ])    
    # test_grid = np.array(
    # [[0,0,9, 0,6,1, 4,0,0]
    # ,[3,0,0, 2,7,0, 0,0,0]
    # ,[4,0,8, 0,3,0, 0,0,1]
    # ,[0,9,4, 0,0,6, 3,0,0]
    # ,[0,8,0, 0,0,5, 0,1,7]
    # ,[0,0,0, 0,0,2, 9,0,0]
    # ,[1,7,6, 9,5,0, 0,0,0]
    # ,[0,3,0, 0,0,8, 0,0,5]
    # ,[0,0,5, 1,0,0, 6,9,0]
    # ])

    sudoku_grid = SudokuGrid(test_grid)
    sudoku_solver = SudokuSolver(sudoku_grid)
    sudoku_solver.simplify_grid()
    #sudoku_solver.brute_force_solve()

    print sudoku_solver.sudoku_grid.to_string()
    #for cand_arr in sudoku_solver.sudoku_grid.candidates:
    #    print cand_arr
    #sudoku_solver.set_grid_from_prompt()

    # for row in range(9):
    #   for col in range(9):
    #       print sudoku_solver.sudoku_grid.get_box_numbers(row, col)


if __name__ == '__main__':
    main()

