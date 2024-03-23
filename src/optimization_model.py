# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 11:53:04 2024

@author: rubir
"""

from pyomo.environ import *
import numpy as np

class OptimizationModel:
    def __init__(self, nob, nPV, nol,PV_threshold, PV_pu, busvolt, voltagelimit, fbus, tbus, r, x, Ppu, Qpu,nonZeroColumnsPpu):
        self.nob = nob
        self.nPV = nPV
        self.nol=nol
        self.PV_threshold = PV_threshold
        self.PV_pu = PV_pu
        self.busvolt = busvolt
        self.voltagelimit = voltagelimit
        self.fbus = fbus
        self.tbus = tbus
        self.r = r
        self.x = x
        self.Ppu = Ppu
        self.Qpu = Qpu
        self.nonZeroColumnsPpu=nonZeroColumnsPpu
        self.model = ConcreteModel()
        
    def setup_model(self):
        m = self.model
        # Variables
        m.cap_p = Var(range(self.nob), range(self.nob), domain=Reals)
        m.sqcurr = Var(range(self.nob), range(self.nob), domain=Reals)
        m.cap_q = Var(range(self.nob), range(self.nob), domain=Reals)
        m.sqvolt = Var(range(self.nob), within=NonNegativeReals)
        m.PV_gen = Var(range(self.nPV), within=NonNegativeReals)
        m.P_new = Var(range(self.nob), domain=Reals)    
        # Constraints
        m.demand = ConstraintList()
        m.PV_constraints = ConstraintList()
        m.voltage_upper = ConstraintList()
        m.voltage = ConstraintList()
        m.active_power_flow_constraints = ConstraintList()
        m.reactive_power_flow_constraints = ConstraintList()
        m.voltage_constraints = ConstraintList()        
        self.define_constraints()        
        # Objective function to maximize PV generation
        m.objective = Objective(expr=sum(m.PV_gen[k] for k in range(self.nPV)), sense=maximize)
    
    def define_constraints(self):
        m = self.model        
        for k in range(self.nPV):
            m.PV_constraints.add(m.PV_gen[k] >= self.PV_threshold)
            m.PV_constraints.add(m.PV_gen[k] <= self.PV_pu)          
        for i in range(self.nob):
            if i in self.nonZeroColumnsPpu:
                # Find the index of PV corresponding to the current bus
                pv_index = list(self.nonZeroColumnsPpu).index(i)
                m.demand.add(m.P_new[i] == self.Ppu[i] - m.PV_gen[pv_index])
            else:
                m.demand.add(m.P_new[i] == self.Ppu[i])                
        for i in range(1):
                 m.voltage.add(m.sqvolt[i] == 1)        
        m.voltage_upper.add(m.sqvolt[self.busvolt-1] <= self.voltagelimit ** 2) 
        for i in range(self.nol):
            from_bus = self.fbus[i]  
            to_bus = (self.tbus[i]) 
            r_val = self.r[i]
            x_val = self.x[i]          
            connected_lines = [j for j in range(self.nol) if self.fbus[j] == self.tbus[i]]
            m.active_power_flow_constraints.add(
                m.cap_p[from_bus, to_bus] == sum(m.cap_p[to_bus, (self.tbus[j]) ] for j in connected_lines) + m.P_new[to_bus]
            )
            m.reactive_power_flow_constraints.add(
                m.cap_q[from_bus, to_bus] == sum(m.cap_q[to_bus, (self.tbus[j]) ] for j in connected_lines) + self.Qpu[to_bus]
            )
            m.voltage_constraints.add(
                m.sqvolt[to_bus] == m.sqvolt[from_bus] - 2 * r_val * m.cap_p[from_bus, to_bus] - 2 * x_val * m.cap_q[from_bus, to_bus]
            )

    def solve(self):
        # Solver setup and solve
        solver = SolverFactory('ipopt')
        solver.solve(self.model)
        