#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 16:37:49 2020

@author: hauke
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy import signal
from scipy import interpolate


def main():
    # gauss_convolution()
    # d2_convolution()
    # wl_convolution
    wl_interpolation()
    # return

def wl_interpolation():
    data = np.loadtxt("./sample files/Asterix1059_1468_processed.csv", skiprows=7, delimiter=",")

    peak = np.loadtxt("./sample files/CH-Peaks_test.dat")
    # Convert angstrom to nm
    peak[:, 0] = peak[:, 0] /10
    # find range of convolution
    wlRange = peak[0, 0], peak[-1, 0]

    plt.plot(*peak.transpose())

    f = interpolate.interp1d(*peak.transpose())
    f = interpolate.interp1d(*peak.transpose(), kind="quadratic")
    f = interpolate.interp1d(*peak.transpose(), kind="cubic")

    newX = np.arange(*wlRange, .05)
    plt.plot(newX, f(newX))

def wl_convolution():

    data = np.loadtxt("./sample files/Asterix1059_1468_processed.csv", skiprows=7, delimiter=",")
    print(data.shape)

    peak = np.loadtxt("./sample files/CH-Peaks.dat")
    # Convert angstrom to nm
    peak[:, 0] = peak[:, 0] /10
    # find range of convolution
    wlRange = peak[0, 0], peak[-1, 0]
    print(peak.shape)

    idx = (data[:, 0] > wlRange[0]) * (data[:, 0] < wlRange[1])
    dataWl = data[idx][:, 0]

    con = np.convolve(dataWl, peak[:, 0], mode="same")
    offset = np.max(dataWl, peak[:, 0]) / 2 + 1

    cx = np.arange(-offset, con.shape[0]-offset)

def d2_convolution():
    hanSize = 50
    sig = np.repeat([0., 1., 0.], 100)
    sig = np.array([[0, 0], [99, 0], [100, 1], [199, 1], [200, 0], [299, 0]])
    win = signal.hann(hanSize)
    xrange = np.arange(hanSize)
    win2D = np.asarray([xrange, win]).transpose()
    filtered = signal.convolve(sig, win2D, mode='same') / sum(win)
    plt.plot(*sig.transpose())
    plt.plot(*win2D.transpose())
    plt.plot(filtered)


def gauss_convolution():
    xy = create_gauss_bell(grid=0.01)
    plt.plot(*xy, label="def")
    coarseGrid = 0.001
    xyCoarse = create_gauss_bell(xLimit=8, grid=coarseGrid, mean=1)
    noise = np.random.normal(size=xyCoarse.shape[1], scale=0.01)
    xyCoarse[1] += noise
    plt.plot(*xyCoarse, label="shifted")
    plt.legend()

    c = np.convolve(xy[1], xyCoarse[1], mode="same")
    print(c.shape)
    print(xy.shape)
    print(xyCoarse.shape)
    offset = max(xy.shape[1], xyCoarse.shape[1]) / 2 + 1
    cx = np.arange(-offset, c.shape[0]-offset) * coarseGrid
    plt.plot(cx, c/50)
    maxIndex = np.argmax(c)
    print(cx[maxIndex])
    print(maxIndex)
    plt.xlim(([-3, 4]))


def create_gauss_bell(xLimit:float=40.0, grid:float=0.002, mean:float=0, std:float=1)->np.ndarray:
    x = np.arange(-xLimit, xLimit, grid)
    #create range of y-values that correspond to normal pdf with mean=0 and sd=1
    y = norm.pdf(x, mean, std)
    xy = np.asarray([x, y])
    return xy


main()