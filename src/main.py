# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 11:54:03 2024

@author: rubir
"""
import sys
import os

from utils.config_loader import load_config
from src.data_loader import DataLoader
from src.optimization_model import OptimizationModel
from src.result_analysis import plot_results
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
def main():
    config_path = os.path.join(project_root, 'config', 'settings.json')
    config = load_config(config_path)
    PV_threshold = config["PV_threshold"]
    busvolt=config["busvolt"]
    Sbase=config["Sbase"]
    voltagelimit=config["voltagelimit"]
    loader = DataLoader(config)
    Ppu,Qpu,nPV ,nonZeroColumnsPpu= loader.load_time_series_load()
    PV_pu = loader.load_PV_data()
    nob,nol, fbus, tbus,r_pu, x_pu=loader.grid_topology()   
    optimization_model = OptimizationModel(nob, nol,nPV, PV_threshold, PV_pu, busvolt, voltagelimit, fbus, tbus, r_pu, x_pu, Ppu, Qpu,nonZeroColumnsPpu)
    optimization_model.setup_model()
    optimization_model.solve()
    plot_results(optimization_model.model, nPV, nob, Sbase)

    
if __name__ == "__main__":
    main()
