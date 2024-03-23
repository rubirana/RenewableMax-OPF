# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 11:54:03 2024

@author: rubir
"""

import matplotlib.pyplot as plt
from math import sqrt

def plot_results(model, nPV, nob,Sbase):
    # Plot PV generation values
    PV_gen_values = [Sbase*model.PV_gen[k].value for k in range(nPV)]
    plt.figure(figsize=(10, 6))
    plt.plot(range(nPV), PV_gen_values, linestyle='-', color='b')
    plt.xlabel('PV Unit Index')
    plt.ylabel('Generation (kW)')
    plt.show()

    # Plot actual voltage values at each node
    voltages = [sqrt(model.sqvolt[i].value) for i in range(nob)]
    plt.figure(figsize=(10, 6))
    plt.plot(range(nob), voltages, linestyle='-', color='r')
    plt.axhline(y=1.05, color='b', linestyle='--', label='Voltage Limit (1.05 p.u.)')
    plt.xlabel('Node Index')
    plt.ylabel('Voltage (p.u.)')
    plt.show()
