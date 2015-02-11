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
        y_model = b0*math.exp(b1*x[i]**b2)
        error += (y[i] - y_model)**2
    return error

def kappa_new_error_simple(params, *args):
    x = args[0]
    y = args[1]
    A, r, c = params
    error = 0.0
    for i in range(len(x)):
        try:
            y_model = A*(x[i]**r) + c
        except:
            print A,x[i],r,c
        error += (y[i] - y_model)**2
    return error

def kappa_new_error_gen(params, *args):
    x = args[0]
    y = args[1]
    K, Q, B, M, v = params
    error = 0.0
    for i in range(len(x)):
        try:
            temp = 1.0/round(v)
            y_model = K/math.pow((1 + Q*math.exp(-B*(x[i] - M))),temp)
        except:
            y_model = 0.0
        error += (y[i] - y_model)**2
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
            y_model = 1.0
        error += (y[i] - y_model)**2
    return error

def kappa_new_error_gompertz(params, *args):
    x = args[0]
    y = args[1]
    A, B, C = params
    error = 0.0
    for i in range(len(x)):
        try:
            y_model = A*math.exp(-B*math.exp(-C*x[i]))
        except:
            y_model = 0.0
        error += (y[i] - y_model)**2
    return error
