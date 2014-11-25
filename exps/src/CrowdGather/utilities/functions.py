__author__ = 'thodrek'

''' Module to define the functions for estimating K and K^prime '''

import math
import sys

def kappa_error(params, *args):
    x = args[0]
    y = args[1]
    b0, b1, b2 = params
    if b1 <= 1e-08:
        b1 = 0.0
    error = 0.0
    for i in range(len(x)):
        try:
            y_model = b0*math.exp(b1*x[i]**b2)
            error += (y[i] - y_model)**2
        except:
            print "Errors", sys.exc_info()[0]
            print b0
            print b1
            print x[i]
            print b2
            print "Error over"
            sys.exit(-1)
    return error


def kappa_new_error(params, *args):
    x = args[0]
    y = args[1]
    A, G, D = params
    error = 0.0
    for i in range(len(x)):
        try:
            y_model = A/(1 + math.exp(-G*(x[i] - D)))
        except:
            y_model = 0.0
        error += (y[i] - y_model)**2
    return error
