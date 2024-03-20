# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 09:40:44 2020
This code is calculating optimal reactive power from charging stations to minimise the losses.
@author: rubir
"""

from matplotlib import pyplot as plt
from math import asin
from numpy import  sqrt, real, imag, pi
from collections import defaultdict, deque
from datafile import load_case
from numpy import inf
from scipy.sparse import dok_matrix, hstack
from  numpy import* 
from pyomo.environ import *
import pandas as pd


import itertools

case = load_case('casecineldi124.m')
G, B = case.G, case.B
branches = case.branch_list
branches_data= case.branch_data_list



cs_bus_index=[77,47]  # New charging station bus index( It is 78 and 48 in actual network but for python index its is 77, 47) 


branches = case.branch_list
limit    = case.current_limit
n = len(case.demands)
s2 = 2**.5
gens = {bus: gen.v for bus, gen in case.gens.items()}
del gens[0]
slots=24

branches_reverse=[]
for i,j in branches:
    jnew=i
    inew=j
    branches_reverse.append((inew,jnew))
branches_combine=branches+branches_reverse
#print(branches_combine) 
nbranch=len(branches)  # Number of branches
# Creating Branch List dictionary  
branch_list_dict ={}
for i in range(nbranch):
    branch_list_dict[i]=branches[i]
    
# Creating Branch List data dictionary  
branch_list_data_dict ={}
for i in range(nbranch):
    branch_list_data_dict[i]=branches_data[i]

branch_index          =    arange(  len(branches)   )             
branch_index_reverse  =    arange(  len(branches), len(branches_combine)  )

#print(len(branches_combine))
branch_index_combine  =    concatenate( ( branch_index ,  branch_index_reverse ) )
#print(branch_index_combine)
c={}
for i in branch_index:    
        c[i]=branches[i]
cd={}
for ii in branch_index_combine:   
        cd[ii]=branches_combine[ii]
voltage_year_list=     []  
reactive_year_list =   []  


def opf(active_power, reactive_power):
    slots=24
    model = ConcreteModel()
    
    model.nodes = range(n)
    model.time = range(slots)
    model.ev =   Var(range(n),model.time)
    model.u = Var(model.nodes, model.time,domain=NonNegativeReals)
    model.R=Var(branch_index_combine,model.time,domain=NonNegativeReals)
    model.I=Var(branch_index_combine,model.time,bounds=(-inf,inf))
    model.currenti=Var(branch_index,model.time,domain=NonNegativeReals)
    model.voltage =ConstraintList()
    model.equalr=ConstraintList()
    model.equali=ConstraintList()
    
    
    
    model.current=ConstraintList()
    model.current2=ConstraintList()
    for t in model.time:
           
       for (i,j),b in zip(branches,branch_index):
                    
            model.current.add(  model.currenti[b,t]==(G[i,j]*G[i,j] +B[i,j]*B[i,j] )*(s2*model.u[i,t]+s2*model.u[j,t]-2* model.R[(b),t])  )
            model.current2.add(  model.currenti[b,t]<= (limit[i,j])**2)


    
    model.reactive_bound= ConstraintList()
    
    
    for t in model.time:
        for i in model.nodes:
            if i==cs_bus_index[0] or i==cs_bus_index[1]:
                
               model.reactive_bound.add(-0.1*sqrt(2**2 - active_power[i][t]**2)<=model.ev[i,t]<= 0.1* sqrt(2**2 - active_power[i][t]**2)     ) 
    
    for t in model.time:
        for bf, br in zip(branch_index ,branch_index_reverse):
            
            model.equalr.add( model.R[br,t]== model.R[bf,t]    )
      
            model.equali.add( model.I[br,t]== model.I[bf,t]    )
    
    for t in model.time:
        for i in range(1):
            model.voltage.add(model.u[i,t] == 1*1/s2)
            
    model.voltage_lower=ConstraintList()
    model.voltage_upper=ConstraintList()
        
    for t in model.time:
      for i in range(1,n):
        if i==cs_bus_index[0] or i==cs_bus_index[1]:
              model.voltage_lower.add( ( 0.94 * 0.94 )/s2 <=   model.u[i,t]  )
              model.voltage_upper.add(  model.u[i,t]<=   ( 1.1 * 1.1 )/s2     )        
    
    model.quadratic=ConstraintList()  
    
    for t in model.time:            
        for (i,j),b in zip(branches_combine,branch_index_combine):
            model.quadratic.add(2*model.u[i,t]*model.u[j,t] >= model.R[b,t]*model.R[b,t] + model.I[b,t]*model.I[b,t])   
    
    s = lambda  i, l: 1 if i < l else -1
    model.real=      ConstraintList() 
    model.reactive=  ConstraintList()
    for t in model.time:         
        for i in range(1, n):                
                ctt=[]
                xt=[]
                k = lambda  i: (l for l in B[i, :].nonzero()[1])
                for l in k(i):           
                    ctt.append(l)                                                                  
                    for b, (g,h) in cd.items():                        
                        if i==g and l==h:                            
                            xt.append(b)                            
                if i==cs_bus_index[1] :
                 
                  model.reactive.add(s2*model.u[i,t]*sum(B[i, x] for x in ctt )+ sum(-B[i,x]*model.R[bh,t] + G[i,x]*s(i,x)*model.I[bh,t] 
                                                        for (x,bh) in zip(ctt,xt) ) == reactive_power[i][t]/10 + model.ev[i,t]
                        )
                elif i==cs_bus_index[0]:
                  model.reactive.add(s2*model.u[i,t]*sum(B[i, x] for x in ctt )+ sum(-B[i,x]*model.R[bh,t] + G[i,x]*s(i,x)*model.I[bh,t] 
                                                        for (x,bh) in zip(ctt,xt) ) == reactive_power[i][t]/10 + model.ev[i,t]
                        )
                else:
                    
                  model.reactive.add(s2*model.u[i,t]*sum(B[i, x] for x in ctt )+ sum(-B[i,x]*model.R[bh,t] + G[i,x]*s(i,x)*model.I[bh,t] 
                                                        for (x,bh) in zip(ctt,xt) ) == reactive_power[i][t]/10 
                        )
                  
                  
                model.real.add(-s2*model.u[i,t]*(sum(G[i, x] for x in ctt))+ sum(G[i,x]*model.R[bh,t] + B[i,x]*s(i,x)*model.I[bh,t]  for (x,bh) in zip(ctt,xt)) == active_power[i][t]/10
                              ) 
                
    resis_list=[]
    for b in branch_index:
        res,react=branch_list_data_dict[b]
       
        resis_list.append(res)           
    
    model.obj = Objective(expr=sum( model.currenti[b,t] *resis_list[b]   for (i,j),b in zip(branches,branch_index)  for t in model.time) , sense=minimize)  

    
    opt = SolverFactory('ipopt')
   
    outputflag=False
    results = opt.solve(model,report_timing=True)   
    
    results.write()
  
    loss_cost=value(model.obj)
    for t in model.time:
      for (i,j),b  in zip(branches,branch_index):
        current=sqrt(value(model.currenti[b,t]) ) 
        #print(current)
    model.obj.display()
      
    u_opt={}
   
    optimal_Q_timeline=[]
    for t in model.time:
            optimal_Q_bus=[]
            for i in [77,47]: 
              cs = 10*value(model.ev[i,t])    
              optimal_Q_bus.append(cs)
            optimal_Q_timeline.append(optimal_Q_bus)
            
    reactive=optimal_Q_timeline
  
    
    for p in model.u:
        u_op={p:model.u[p].value}
        u_opt.update(u_op)
    V = dok_matrix((n, slots))
    for (i) in u_opt:  
        q,t=i
        V[q,t]= (sqrt(sqrt(2) * u_opt[i] )) 
   
    yt=[]
    
    for i in range(0,n):
        xt=[]
        for t in range(0,slots):
            x=(V[i,t]) 
            xt.append(x)
        yt.append(xt)     
    return yt, reactive, loss_cost


loss_cost_list=[]
voltage_years=[]
reactive_power_years=[]
active_power_original=[]
Reactive_power_original=[]
years=5
list_a = range(years)
fn=[]
old_string = "Sheet1"
for i in range(1,years+1):
   
   x=str(i)

   string_list = list(old_string)
   string_list[5] = x


   new_string = "".join(string_list)

   
   fn.append(new_string)



active = pd.ExcelFile('Active_load.xls')
reactive=pd.ExcelFile('ReActive_load.xls')
for y,s in (zip(list_a, fn)):
    
    df1 = pd.read_excel(active, s)
    df2 = pd.read_excel(reactive, s)
    active_load_year=df1.values.tolist()
    reactive_load_year =df2.values.tolist()  
    for t in range(slots):        
                reactive_load_year[47][t]=0
                reactive_load_year[77][t]=0 
    voltage_year_list, reactive_year_list,loss_cost=opf(active_load_year, reactive_load_year)
    loss_cost_list.append(loss_cost)
    df = pd.DataFrame(voltage_year_list)      
    voltage_years.append(df)
    df2 = pd.DataFrame(reactive_year_list)
    
    df3=     pd.DataFrame(loss_cost_list)
    df3.to_excel(r'loss_cost.xlsx', index = False)
    reactive_power_years.append(df2)
    


Excelwriter = pd.ExcelWriter("optimal_Q.xlsx",engine="xlsxwriter")

# loop process the list of dataframes
for i, df in enumerate (reactive_power_years):
    df.to_excel(Excelwriter, sheet_name="Sheet" + str(i+1),index=False)
#And finally save the file
Excelwriter.save()

Excelwriter = pd.ExcelWriter("optimal_v.xlsx",engine="xlsxwriter")

# loop process the list of dataframes
for i, df in enumerate (voltage_years):
    df.to_excel(Excelwriter, sheet_name="Sheet" + str(i+1),index=False)
#And finally save the file
Excelwriter.save()




    