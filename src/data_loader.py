# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 11:54:03 2024

@author: rubir
"""

import pandas as pd
from datafile import load_case
import numpy as np
import os
class DataLoader:
   
    def __init__(self, config):
        self.config = config
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    def get_full_path(self, relative_path):
        return os.path.join(self.project_root, relative_path)
    def load_time_series_load(self):
        time_series_file = self.get_full_path(self.config["time_series_file"])

        time_series_load = pd.read_excel(time_series_file, header=None)
        time_series_active = time_series_load.iloc[0:8760, 0] / time_series_load.iloc[0:8760, 0].max()
        time_series_reactive = time_series_load.iloc[0:8760, 1] / time_series_load.iloc[0:8760, 1].max()

        # Load peak load data
        active_load_peak, reactive_load_peak = self.load_peak_load_data()

        # Reshape and multiply by peak loads
        active_load = pd.DataFrame(time_series_active.values.reshape(-1, 1) * active_load_peak.values, columns=active_load_peak.index)
        reactive_load = pd.DataFrame(time_series_reactive.values.reshape(-1, 1) * reactive_load_peak.values, columns=reactive_load_peak.index)

        # Slice based on start_hour and data_hour
        start_hour = self.config["start_hour"]
        data_hour = self.config["data_hour"]
        Sbase=self.config["Sbase"]
        P = active_load.iloc[start_hour-1 : start_hour+23,:]
        Q = reactive_load.iloc[start_hour-1 : start_hour+23,:]
        # Find non-zero columns in Ppu
        nonZeroColumnsPpu = np.where(np.any(P != 0, axis=0))[0]
        nPV = len(nonZeroColumnsPpu)
        # Problem hour data
        Ppu = P.iloc[data_hour-1, :] / Sbase
        Qpu = Q.iloc[data_hour-1, :] / Sbase
        return Ppu, Qpu,nPV,nonZeroColumnsPpu

    def load_peak_load_data(self):
        peak_data_file = self.get_full_path(self.config["peak_data_file"])

        peak_load_data = pd.read_excel(peak_data_file, header=None)
        
        active_load_peak = peak_load_data.iloc[:, 0]
        reactive_load_peak = peak_load_data.iloc[:, 1]

        # Squeeze if they are DataFrames
        if isinstance(active_load_peak, pd.DataFrame):
            active_load_peak = active_load_peak.squeeze()
        if isinstance(reactive_load_peak, pd.DataFrame):
            reactive_load_peak = reactive_load_peak.squeeze()

        return active_load_peak, reactive_load_peak

    def load_PV_data(self):
        PV_data_file = self.get_full_path(self.config["PV_data_file"])
        
        df_PV = pd.read_excel(PV_data_file, usecols='C', skiprows=4, nrows=8760, header=None).values.flatten() * (self.config["size"])

        # Slice PV data based on start_hour for 24 hours period
        start_hour = self.config["start_hour"]
        Sbase=self.config["Sbase"]
        data_hour = self.config["data_hour"]
        PV_profile = df_PV[start_hour-1 : start_hour+23]
        PV_pu = PV_profile[data_hour-1] / Sbase
        return PV_pu
   
    
    
    def grid_topology(self):
        case_file_path=self.get_full_path(self.config["case_file"])
        
        case = load_case(case_file_path)  # Assuming load_case is a function you have defined to load case data.
        V_base=self.config["V_base"]
        Base_KVA=self.config["Base_KVA"]
        Z_base=(V_base*1000)**2 / (Base_KVA * 1000)

        G = case.G
        branches = case.branch_list
        branches_data= case.branch_data_list

        branches_data = [(x/Z_base, y/Z_base) for x, y in branches_data]  ## Per unit conversion
        ##Convert branches_data to pu 
        n = len(case.demands)
        # Convert fbus and tbus to integers
        fbus, tbus = zip(*branches)


        r_pu,x_pu=zip(*branches_data)
        nol= len(branches)
        nob=n
        return nob,nol, fbus, tbus,r_pu, x_pu   