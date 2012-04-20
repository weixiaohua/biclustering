'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import numpy
import random
from itertools import combinations

# A, k, m
# B, l, n


# Define a stability threashold 
STABILITY_THREASHOLD = 1000 

# Define the size and shape of the test matrix.
SIZE  = 10
SHAPE = ( SIZE, SIZE ) 

# Populate the test matrix with gaussian noise on (0,1)
X = numpy.random.normal( size=SHAPE )
X += 1
X *= 0.5

# Add a feature to detect
FEATURE = numpy.zeros( SHAPE )
FEATURE[0:SIZE/2,0:SIZE/2] = 0.5
X += FEATURE

# Get m and n
m, n = X.shape # rows, columns


# Select initial k and l from {1...[m/2]} and {1...[n/2]} respectively (at random)
def get_k_and_l( ):
    k = random.randint( 1, int( m/2 ) )
    l = random.randint( 1, int( n/2 ) )
    return ( k, l )

# Start with a random B ( matrix of l cols )
def get_B_candidate_at_random( X, l, n, sets_checked ):
    l_zeros = numpy.zeros( ( 1, l ), dtype=int )
    l_rands = numpy.random.random( ( 1, l ) )
    l_rands *= n
    l_zeros += l_rands
    which_l_cols = l_zeros

    sets = 0
    while tuple( which_l_cols[ 0 ] ) in sets_checked:
        l_zeros = numpy.zeros( ( 1, l ), dtype=int )
        l_rands = numpy.random.random( ( 1, l ) )
        l_rands *= n
        l_zeros += l_rands 
        which_l_cols = l_zeros
        sets += 1
        if sets >= STABILITY_THREASHOLD:
            return False 
        print "Fetching unchecked set..."
    
    sets_checked.append( tuple( which_l_cols[ 0 ] ) )

    B = numpy.zeros( X.shape ) 
    for i in which_l_cols:
        B[:,i] = X[:,i]

    return B 

# Find the best A ( matrix of k rows ) for the chosen B
def get_A_candidate_at_random( X, k, m, sets_checked ):
    k_zeros = numpy.zeros( ( 1, k ), dtype=int )
    k_rands = numpy.random.random( ( 1, k ) )
    k_rands *= m
    k_zeros += k_rands
    which_k_rows = k_zeros 

    sets = 0
    while tuple( which_k_rows[ 0 ] ) in sets_checked: 
        k_zeros = numpy.zeros( ( 1, k ), dtype=int )
        k_rands = numpy.random.random( ( 1, k ) )
        k_rands *= m
        k_zeros += k_rands
        which_k_rows = k_zeros 
        sets += 1
        if sets >= STABILITY_THREASHOLD:
            return False
        print "Fetching unchecked set..." 
    
    sets_checked.append( tuple( which_k_rows[ 0 ] ) )
   
    A = numpy.zeros( X.shape )
    for i in which_k_rows:
        A[i,:] = X[i,:]

    return A 
        
def score_A_and_B( A, B, X ):
    C = A * B
    indicies = C.nonzero( )
    entries = A[ indicies ]
    total = numpy.sum( entries )
    return total
     
def get_A( k, l, B, X ):
    running_max = 0
    winner = None
    a_sets_checked = [ ]
    for iteration in range( 0, STABILITY_THREASHOLD / 10 ):
        A = get_A_candidate_at_random( X, k, m, a_sets_checked )
        total = score_A_and_B( A, B, X )
        if total > running_max:
            running_max = total
            winner = A
    return winner

def get_B( k, l, A, X ):
    running_max = 0
    winner = None
    b_sets_checked = [ ]
    for iteration in range( 0, STABILITY_THREASHOLD / 10 ):
        B = get_B_candidate_at_random( X, l, n, b_sets_checked )
        total = score_A_and_B( A, B, X )
        if total > running_max:
            running_max = total
            winner = B
    return winner

def get_best_A( k, l, B, X ):
    running_max = 0
    winner = None
    combos = combinations( range( 0, m ), k )  
    for combo in combos:
        print combo

def have_converged( A, B ):
    return sum( A - B ) == 0

def build_matrix_from_k_rows_of_X( k_rows, X ):
    M = numpy.zeros( X.shape )
    for row in k_rows:
        M[row,:] = X[row,:]
    return M

def build_matrix_from_l_cols_of_X( l_cols, X ):
    M = numpy.zeros( X.shape )
    for col in l_cols:
        M[:,col] = X[:,col]
    return M

def get_k_rows_with_largest_sum_over_columns_of_B( k, B ):
    column_list = range( 1, m )
    winning_total = 0
    winner = None
    for max_candidate in combinations( column_list, k ):
        A = build_matrix_from_k_rows_of_X( max_candidate, X )
        score = sum_rows_of_A_over_cols_of_B( A, B )
        if score > winning_total:
            winner = A
            winning_total = score
    return A


def get_l_columns_with_largest_sum_over_rows_of_A( l, A ):
    row_list = range( 1, n )
    winning_total = 0
    winner = None
    for max_candidate in combinations( row_list, l ):
        B = build_matrix_from_l_cols_of_X( max_candidate, X )
        score = sum_cols_of_B_over_rows_of_A( A, B )
        if score > winning_total:
            winner = B
            winning_total = score
    return B

def get_intersection( A, B, X ):
    intersection = numpy.zeros( X.shape )
    C = A * B
    indicies = C.nonzero( )
    intersection[ indicies ] = A[ indicies ]
    return intersection 
    

def get_submatrix( X, k=None, l=None ):
    stability_counter = 0
    highest_score = -100000
    k, l = get_k_and_l( )
    a_sets_checked = [ ]
    b_sets_checked = [ ]
    B = get_B_candidate_at_random( X, l, n, b_sets_checked )
    while stability_counter < STABILITY_THREASHOLD:
        print "Iterating... " + str( stability_counter )
        A_candidate = get_A_candidate_at_random( X, k, m, a_sets_checked )
        if A_candidate is False:
            return get_intersection( A, B, X )
        #A_candidate = get_A( k, l, B, X )
        score = score_A_and_B( A_candidate, B, X )
        if score > highest_score:
            highest_score = score
            A = A_candidate.copy( )
            stability_counter = 0
        B_candidate = get_B_candidate_at_random( X, l, n, b_sets_checked )
        if B_candidate is False:
            return get_intersection( A, B, X )
        #B_candidate = get_B( k, l, A, X )
        score = score_A_and_B( A, B_candidate, X )
        if score > highest_score:
            highest_score = score
            B = B_candidate.copy( )
            stability_counter = 0
        stability_counter += 1
    print "k, l: " + str( k ) + ", " + str( l )
    return get_intersection( A, B, X )

if __name__ == '__main__':
    print get_submatrix( X )
