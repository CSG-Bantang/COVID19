#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 15:42:28 2020

@author: rxander
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import scipy.integrate as spi
from matplotlib.colors import LinearSegmentedColormap
import networkx as nx
from scipy.stats import truncnorm
import pandas as pd

class SICRD():
    def __init__(self, end=2, odmat = np.eye(1), brgy = 0, S_mat = np.array([1-1e-6]), 
                 I_mat = np.array(1e-6), C_mat = np.zeros(1), R_mat = np.zeros(1), 
                 D_mat = np.zeros(1), f_mat = np.array([3]), q_mat = np.array([0.05]), 
                 h_mat = np.array([0.1]), b=0.082, w=0.035, z=0.001, r=0.0, m=0.002):
        self.end = end
        self.odmat, self.brgy = odmat, brgy
        self.b, self.w, self.z, self.r, self.m = b, w, z, r, m
        self.f, self.q, self.h = f_mat, q_mat, h_mat
        if type(S_mat) == int or type(S_mat) == float:
            self.S, self.I, self.C, self.R, self.D = np.array([S_mat]), np.array([I_mat]), np.array([C_mat]), np.array([R_mat]), np.array([D_mat])
        else:
            self.S, self.I, self.C, self.R, self.D = S_mat, I_mat, C_mat, R_mat, D_mat
    def odes(self, INPUT, t):
        Sb, Ib, Cb, Rb, Db = INPUT
        qI = (1-self.q)*self.I
        hC = (1-self.h)*self.C
        theta = np.sum(self.b*self.f*self.odmat[:,self.brgy]*
                       self.S*np.matmul(self.odmat, qI+hC))
        dSdt = -theta + self.r*(Ib + Cb)
        dIdt = +theta -(self.w+self.r+self.m+self.z)*Ib
        dCdt = +self.w*Ib - (self.r+self.z+self.m)*Cb
        dRdt = self.z*(Ib + Cb)
        dDdt = self.m*(Ib + Cb)
        OUTPUT = [dSdt, dIdt, dCdt, dRdt, dDdt]
        return OUTPUT
    def solver(self):
        start, self.end, increment = 1,2, 1
        trange = np.arange(start, self.end+increment, increment)
        INP = [self.S[self.brgy], self.I[self.brgy], self.C[self.brgy], self.R[self.brgy], self.D[self.brgy]]
        result = spi.odeint(self.odes, INP, trange)
        return result[1]

## Define the date axis
dstart = dt.datetime(2020,3,4)
dend = dt.datetime(2020,5,15)
ddelta = dt.timedelta(days=1)
drange = mdates.drange(dstart, dend, ddelta)
duration = len(drange)-1

## Date axis formatter
months = mdates.MonthLocator()
days = mdates.DayLocator(interval = 1)
mday_fmt = mdates.DateFormatter('%b %d')

## Create Blue-Red and Blue-Green CMAP
cdict1 = {'red':   ((0.0, 0.0, 0.0),
                   (0.5, 0.0, 0.1),
                   (1.0, 1.0, 1.0)),
         'green': ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),
         'blue':  ((0.0, 0.0, 1.0),
                   (0.5, 0.1, 0.0),
                   (1.0, 0.0, 0.0))}
blue_red = LinearSegmentedColormap('BlueRed', cdict1)

popmat = np.loadtxt('populationQC.txt')
L = len(popmat)
ODmat09 = np.load('QC09-pnorm.npy').T
ODmat17 = np.load('QC17-pnorm.npy').T

ODmat09 = ODmat09/np.sum(ODmat09, axis=0)
ODmat17 = ODmat17/np.sum(ODmat17, axis=0)
np.nan_to_num(ODmat09, 0)
np.nan_to_num(ODmat17, 0)

fmat = np.asarray([3]*L)
qmat = np.asarray([0.05]*L)
hmat = np.asarray([0.1]*L)

I0 = np.zeros(L, dtype=float)
I0[18] = 3
I0[50] = 1
I0[24] = 2
S0 = popmat-I0
C0 = np.zeros(L, dtype=float)
R0 = np.zeros(L, dtype=float)
D0 = np.zeros(L, dtype=float)
S,I,C,R,D = np.zeros((duration+1,L)), np.zeros((duration+1,L)), np.zeros((duration+1,L)), np.zeros((duration+1,L)), np.zeros((duration+1,L))
S[0], I[0], C[0], R[0], D[0] = S0, I0, C0, R0, D0
matS = [100*S0/popmat]
matI = [100*I0/popmat]
matC = [100*C0/popmat]
matR = [100*R0/popmat]
matD = [100*D0/popmat]
for time in range(duration):
    date1, date2 = dt.datetime(2020,3,9), dt.datetime(2020,3,17)
    if time < np.where(drange==mdates.date2num(date2))[0][0]:
        odmat = ODmat09.copy()
    else:
        odmat = ODmat17.copy()
    for brgy in range(L):
        RES = SICRD(odmat = odmat, brgy = brgy, S_mat = S0/popmat, I_mat = I0/popmat,
                    C_mat = C0/popmat, R_mat = R0/popmat, D_mat = D0/popmat,
                    f_mat = fmat, q_mat = qmat, h_mat = hmat).solver()
        S0[brgy], I0[brgy], C0[brgy], R0[brgy], D0[brgy] = RES*popmat[brgy]
    matS.append(100*np.round(S0,0)/popmat)
    matI.append(100*np.round(I0,0)/popmat)
    matC.append(100*np.round(C0,0)/popmat)
    matR.append(100*np.round(R0,0)/popmat)
    matD.append(100*np.round(D0,0)/popmat)
    S[time+1] = S0
    I[time+1] = I0
    C[time+1] = C0
    R[time+1] = R0
    D[time+1] = D0
arrmat = np.asarray(np.add(matC,matI))
plt.figure()
ax = plt.gca()
im = ax.matshow(arrmat, vmin=0, vmax=100, cmap = blue_red, extent = [0,L,drange[0], drange[duration]], aspect='auto', origin='lower')
plt.xlabel('Barangay ID')
ax.yaxis_date()
ax.xaxis.set_label_position('top') 
ax.yaxis.set_major_locator(months)
ax.yaxis.set_major_formatter(mday_fmt)
ax.invert_yaxis()
cbar = plt.colorbar(im)
cbar.set_label('Population Percentage of (I+C)')
plt.tight_layout()
plt.savefig('single-vector-mobile.png', dpi=100, bbox_to_inches='tight')
fig, ax = plt.subplots()
ave, count = np.zeros(72), 0
for brgy in range(L):
    ave+=popmat[brgy]*arrmat[:,brgy]
    count+=1
    ax.semilogy(drange,popmat[brgy]*arrmat[:,brgy], color='gray')
aver = ave/count
ax.semilogy(drange, aver, color='red', linewidth = 4, label = 'Average')
ax.xaxis.set_major_locator(months)
ax.xaxis.set_major_formatter(mday_fmt)
plt.title('Total Cases per Barangay')
plt.ylabel('Population')
plt.legend()
plt.tight_layout()
plt.savefig('single-vector-mobile-semilogy.png', dpi=100, bbox_to_inches='tight')
#print(np.sum((S0,I0,R0,D0,C0)))
#header = np.array(range(1, L+1))
np.savetxt('Spop.txt',S*100/popmat, delimiter=',', fmt='%1.1f')
np.savetxt('Ipop.txt',(I)*100/popmat, delimiter=',', fmt='%1.1f')
np.savetxt('Cpop.txt',C*100/popmat, delimiter=',', fmt='%1.1f')
np.savetxt('Rpop.txt',R*100/popmat, delimiter=',', fmt='%1.1f')
np.savetxt('Dpop.txt',D*100/popmat, delimiter=',', fmt='%1.1f')