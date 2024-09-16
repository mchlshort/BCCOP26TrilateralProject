'''
Created on 24th September 2021
Last Modified in March 2023

This script presents the mathematical optimisation formulation for an energy planning scenario in a specific geographical region or district.
Renewable energy and fossil-based sources make up the power generation in a specific geographical region or district. 
Each period consists of its respective energy demand and CO2 emission limit.
EP-NETs, EC-NETs, CCS/CCSU and Carbon Trading may be utilised to achieve the CO2 emission limit for each period.
This energy planning mathematical formulation may be optimised subject to either a mininum cost or minimum emission objective function. 
There is an addtional formulation to optimize for maximum profit which satisfies both emission targets and budget contraints, which proves the feasibility of data/model, and provides effective initial values.

@author: Gul, Purusothmn, Dr Michael Short, Prof Dr Dominic C.Y.F.
'''
import os 

path = os.chdir(r'C:\Users\pc\Desktop\DECO2 v2023\Direct Optimization Model') 

cwd = os.getcwd()

import DO_EP_Optimal_Decarbonisation_Model_Python
