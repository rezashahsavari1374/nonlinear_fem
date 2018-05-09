#coding:utf8
#***************************mod.py***************************
# Author    : Yuichiro SUGA
# Email     : yuichiro.suga@centraliens-lille.org
# Created   : 2018-05-08 AM 11:42:06
# Modified  : 
# Main module for non-linear FEM. Try to break codes down to 
# smaller files
#************************************************************
import itertools
import numpy.linalg as LA

import config as cfg


def simple_product(i,j):
    return itertools(range(i), range(j))


def kron_delta(i, j):
    if i == j:
        return 1
    else:
        return 0


def zero_matrix(i,j):
    a = np.zeros([i,j],dtype=np.float128)
    a = np.matrix(a)
    return a
    
#Shape function
# x @ Position vector as argument
# p @ Position vector of node1
# q @ Position vector of node2
# Attribute 0->x; 1->y
# Example x(x, y) -> (x[0], x[1])
# FIXME コメント書き直し
def Ni(element, x):
    if cfg.SHAPE == 3:
        s_e = get_prlgrm(p1, p2, p3)
        #Eq. 1.50 (rf. Nonlinear FEM, p24)
        N = 1/s_e * ((p2[0]*p3[1]-p3[0]*p2[1])
                + (p2[1] - p3[1])*x[0]
                + (p3[0] - p2[0])*x[1])
    elif cfg.SHAPE == 4:
        #FIXME verify mapping from spatial coordinate to natural coordinate
        cof = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        #p1, p2, p3, p4 = element[1:5]
        #N = [ 1/4 * (1 + xi[0]*node[pi-1][0]) * (1 + xi[1]*node[pi-1][1])
        #   for xi ,pi in zip(cof, element[1:5]) ]
        N = [ 1/4 * (1 + xi[0]*x[0]) * (1 + xi[1]*x[1]) for xi in cof ]
    else:
        raise NameError('Constant "SHAPE" is invalid!')
    return N


#Get area of parallelogram p1-p2-p3
# Refers nodes in *anti-clockwise*
def get_prlgrm(p1, p2, p3):
    area = ( p1[0]*p2[1] + p2[0]*p3[1] + p3[0]*p1[1]
            - p1[0]*p3[1] - p2[0]*p1[1] - p3[0]*p2[1] )
    if area < 0:
        raise NameError('Clockwise triangle, Element area got negative')
    return area


#Current material point: X
def get_N(X):
    N = np.zeros((DIMENSION, SHAPE * DIMENSION))
    N = [[Ni(X, p2, p3), .0],
         [.0, Ni(X, p2, p3)],
         [Ni(X, p3, p1), .0],
         [.0, Ni(X, p3, p1)]
         [Ni(X, p1, p2), .0],
         [.0, Ni(X, p1, p2)]]
    return N


#B Matrix
#   @i_element; Index of element
#   @node     ; Set of nodes
#   @x        ; X as global coordinate
#   @e        ; Eta as local coordinate
# This function varies depending on the number of node
# which consits of one element for each model
def b_matrix(i_element, node, x, e):
    b_m = zero_matrix(3,8)

    #Nodal index which consist of the element
    i, j, k, l = node[:,i_element] -1
    xi  = zero_matrix(2,4)
    xi  = np.matri([x[:,i], x[:,j], x[:,k], x[:,l]]) 
    print(xi)

    #dN/da, dN/db
    dNi_dai = zero_matrix(2,4)
    #dNi_db = np.zeros([4], dtype=np.float128)
    dNi_dai[0,0] = -0.25*(1.0-b)
    dNi_dai[0,1] =  0.25*(1.0-b)
    dNi_dai[0,2] =  0.25*(1.0+b)
    dNi_dai[0,3] = -0.25*(1.0+b)
    dNi_dai[1,0] = -0.25*(1.0-a)
    dNi_dai[1,1] = -0.25*(1.0+a)
    dNi_dai[1,2] =  0.25*(1.0+a)
    dNi_dai[1,3] =  0.25*(1.0-a)
    
    #Inverse of Jaconbi matrix 
    j_m = zero_matirx(2,2)
    #FIXME Can be written more more easily?
    #Write down elements, can be ortho production
    #for i in range(4): #Nb of node in one element
    #    j_m[0,0] += dNi_dai[0,i]*x[0,i]
    #    j_m[0,1] += dNi_dai[0,i]*x[1,i]
    #    j_m[1,0] += dNi_dai[1,i]*x[0,i]
    #    j_m[1,1] += dNi_dai[1.i]*x[1,i]
    j_m = dNi_dai * x.T
    # inverse J
    j_m = j_m.I
    print(j_m)   #XXX Validation
    
    #[dN/dx] = [J] * [dN/da]
    dNi_dxi = zero_matrix(2,4)
    dNi_dxi = j_m * dNi_dai

    #[B]=[dN/dx][dN/dy]
    #Can be written shorter with NumPy!
    #for i,j in simple_product(2, 4):
    for i in range(4)
        bm[0,i*2  ]= dNi_dxi[0,i    ] 
        bm[1,i*2+1]= dNi_dxi[1,i*2+1] 
        bm[2,i*2  ]= dNi_dxi[1,i    ]
        bm[2,i*2+1]= dNi_dxi[0,i*2+1]
    return b_m


#Eq 1.52
#def u(x, y, element):
#    u = .0
#    for i in range(SHAPE):
#        u += ui(x,y) * Ni(x,y)
#    return u


#Eq. 3.167 p.125
#u2 : strain for next step
#u1 : strain for current step
#u0 : strain for one before step
def eq_of_motion(node):
    global h1, h2, h3
    h1 = kinematic_coefficient.h1()
    h2 = kinematic_coefficient.h2()
    h3 = kinematic_coefficient.h3()
    u2[i] = (h2*u1[i] + h3*u0[i]) + (P[node][i] - F[node][i])/h1
    return u2
