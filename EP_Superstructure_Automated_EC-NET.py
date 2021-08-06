'''
Created on 19th July 2021

Energy Planning Scenario in Pyomo

This script presents the mathematical formulation for an energy planning 
scenario in a specific geographical region or district. Renewable energy 
sources and fossil-based source such as coal, oil and natural gas, 
each with its respectively energy contribution and carbon intensity make up 
the power generation in a specific region or district. Each period consists 
of its respective energy demand and carbon emission limit. 
NETs are utilised to achieve the emission limit.

@author: Purusothmn, Dr Michael Short

'''
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import pandas as pd

'''
The plant data represents the CCS and carbon intensity data for power plant s
'''

plant_data = {
    'Plant_1'  : {  'Fuel' : 'REN',
                    'LB'   : 10,
                    'UB'   : 40,        
                    'CI'   : 0,
                    'RR'   : 0,
                    'X'    : 0,
                    'Cost' : 155,
                    'Cost_CCS' : 0}, 
                   
    'Plant_2'  : {  'Fuel' : 'NG',
                    'LB'   : 0,
                    'UB'   : 40,
                    'CI'   : 0.5,
                    'RR'   : 0.85,
                    'X'    : 0.15,
                    'Cost' : 104,
                    'Cost_CCS' : 141},
                    
    'Plant_3'  : {  'Fuel' : 'NG',
                    'LB'   : 0,
                    'UB'   : 40,
                    'CI'   : 0.5,
                    'RR'   : 0.85,
                    'X'    : 0.15,
                    'Cost' : 104,
                    'Cost_CCS' : 141},
                   
    'Plant_4'  : {  'Fuel' : 'NG',
                    'LB'   : 0,
                    'UB'   : 40,
                    'CI'   : 0.5,
                    'RR'   : 0.85,
                    'X'    : 0.15,
                    'Cost' : 104,
                    'Cost_CCS' : 141}, 
                   
    'Plant_5'  : {  'Fuel' : 'OIL',
                    'LB'   : 0,
                    'UB'   : 10,
                    'CI'   : 0.8,
                    'RR'   : 0.85,
                    'X'    : 0.15,
                    'Cost' : 202,
                    'Cost_CCS' : 280},
                   
    'Plant_6'  : {  'Fuel' : 'COAL',
                    'LB'   : 0,
                    'UB'   : 20,
                    'CI'   : 1,
                    'RR'   : 0.85,
                    'X'    : 0.15,
                    'Cost' : 51,
                    'Cost_CCS' : 82},
                   
    'Plant_7'  : {  'Fuel' : 'COAL',
                    'LB'   : 0,
                    'UB'   : 20,
                    'CI'   : 1,
                    'RR'   : 0.85,
                    'X'    : 0.15,
                    'Cost' : 51,
                    'Cost_CCS' : 82}, 
                   
    'Plant_8'  : {  'Fuel' : 'COAL',
                    'LB'   : 0,
                    'UB'   : 20,
                    'CI'   : 1,
                    'RR'   : 0.85,
                    'X'    : 0.15,
                    'Cost' : 51,
                    'Cost_CCS' : 82}                    
    }

s = plant_data.keys()

prd = [1, 2, 3]
Demand = [60, 75, 90]
Limit = [15, 8, 3]
EC_NET_CI = [-0.6, -0.6, -0.6]
Cost_EC_NET = [180, 180, 180]
Comp_CI = [0, 0, 0]
Cost_Comp = [155, 155, 155]

numperiods = len(prd) + 1
period_data_dict = {}

for (i,D,L,ECI,CEC,CI,CC) in zip(prd, Demand, Limit, EC_NET_CI, Cost_EC_NET, Comp_CI, Cost_Comp):    
    period_data_dict[i]= {'Demand' : D, 
                          'Emission_Limit' : L, 
                          'EC_NET_CI' : ECI, 
                          'Cost_EC_NET' : CEC,
                          'Comp_CI' : CI,
                          'Cost_Comp' : CC}
    
def EP_Period(plant_data,period_data): 
    model = pyo.ConcreteModel()
    model.S = plant_data.keys()
    model.plant_data = plant_data
    model.period_data = period_data
       
    #LIST OF VARIABLES
    
    #This variable determines the deployment of energy sources in power plant s
    model.energy = pyo.Var(model.S, domain = pyo.NonNegativeReals)
    
    #This variable determines the carbon intensity of power plant s with CCS deployment for each period
    model.CI_RET = pyo.Var(model.S, domain = pyo.NonNegativeReals)
    
    #Binary variable for CCS deployment in power plant s for each period
    model.B = pyo.Var(model.S, domain = pyo.Binary)
    
    #This variable represents the extent of CCS retrofit in power plant s for each period
    model.CCS = pyo.Var(model.S, domain = pyo.NonNegativeReals) 
    
    #This variable determines the net energy available from power plant s without CCS deployment for each period
    model.net_energy = pyo.Var(model.S, domain = pyo.NonNegativeReals)
    
    #This variable determines the net energy available from power plant s with CCS deployment for each period
    model.net_energy_CCS = pyo.Var(model.S, domain = pyo.NonNegativeReals)
    
    #This variable represents the minimum deployment of EC_NETs for each period 
    model.EC_NET = pyo.Var(domain = pyo.NonNegativeReals)
    
    #This variable determines the minimum deployment of renewable compensatory energy for each period
    model.comp = pyo.Var(domain = pyo.NonNegativeReals)

    #This variable determines the final total CO2 emission after energy planning for each period
    model.new_emission = pyo.Var(domain = pyo.NonNegativeReals)

    #This variable determines the total energy cost for each period
    model.sum_cost = pyo.Var(domain = pyo.NonNegativeReals)    
          
    #OBJECTIVE FUNCTION
    
    #The objective function minimises the cumulative extent of CCS retrofit, thus minimising the NET requirement
    model.obj = pyo.Objective(expr = model.sum_cost, sense = pyo.minimize)
   
    #CONSTRAINTS
    
    model.cons = pyo.ConstraintList()

    model.cons.add(sum(model.energy[s] for s in model.S) == model.period_data['Demand'])
    
    for s in model.S:
        #Calculation of carbon intensity for CCS retrofitted fossil-based sources
        model.cons.add((model.plant_data[s]['CI'] * (1 - model.plant_data[s]['RR']) / (1 - model.plant_data[s]['X'])) == model.CI_RET[s])
        
        #The deployment of energy source in power plant s should at least satisfy the lower bound
        model.cons.add(model.energy[s] >= model.plant_data[s]['LB'])
        
        #The deployment of energy source in power plant s should at most satisfy the upper bound
        model.cons.add(model.energy[s] <= model.plant_data[s]['UB'])
    
        #The extent of CCS retrofit on fossil-based sources should never exceed the available energy
        model.cons.add(model.CCS[s] <= model.energy[s])
        
        #Determine the net energy available from fossil-based sources with CCS retrofit
        model.cons.add(model.CCS[s] * (1 - model.plant_data[s]['X']) * model.B[s] == model.net_energy_CCS[s])
        
        #The summation of energy contribution from each source with and without CCS retrofit must equal to individual energy contribution
        model.cons.add(model.net_energy[s] + (model.CCS[s] * model.B[s]) == model.energy[s]) 
    
        if 'REN' in model.plant_data[s].values():
            model.CCS[s].fix(0)
   
    #Total energy contribution from all energy sources to satisfy the total demand
    model.cons.add(sum(((model.net_energy[s]) + (model.net_energy_CCS[s] * model.B[s])) for s in model.S) + model.comp == model.period_data['Demand'] + model.EC_NET) 
    
    #The total CO2 load contribution from all energy sources must satisfy most the CO2 emission limit after energy planning 
    model.cons.add(sum((model.net_energy[s] * model.plant_data[s]['CI']) + (model.net_energy_CCS[s] * model.CI_RET[s]) for s in model.S)
               + (model.EC_NET * model.period_data['EC_NET_CI']) 
               + (model.comp * model.period_data['Comp_CI']) == model.new_emission)

    #The summation of cost for each power plant s should equal to the total cost of each period
    model.cons.add(sum((model.net_energy[s] * model.plant_data[s]['Cost']) + (model.net_energy_CCS[s] * model.plant_data[s]['Cost_CCS'] * model.B[s]) for s in model.S)
               + (model.EC_NET * model.period_data['Cost_EC_NET'])
               + (model.comp * model.period_data['Cost_Comp']) == model.sum_cost) 
    
    #Total CO2 load contribution from all energy sources to satisfy the emission limit
    model.cons.add(model.new_emission == model.period_data['Emission_Limit'])  
        
    return model

#Creating a list with 3 strings
block_sets = list(range(1, numperiods, 1))

#Adding the models to a dictionary to be accessed inside the function
EP = dict()
for i in range(1, numperiods, 1):
    EP[block_sets[i-1]] = EP_Period(plant_data, period_data_dict[i])

Full_model = pyo.ConcreteModel()

'''
This function defines each block - the block is model m containing all equations and variables
It needs to be put in the right set (block_sets) with objective function turned off
'''
def build_individual_blocks(model, block_sets):
    model = EP[block_sets]
    model.obj.deactivate()
    model.del_component(model.obj)
    return model

#Defining the pyomo block structure with the set block sets and rule to build the blocks
Full_model.subprobs = pyo.Block(block_sets, rule = build_individual_blocks)

'''
The blocks are linked such that the extent of CCS retrofit on source i at period t + 1
should at least match the extent of CCS retrofit on source i at period t
'''

def linking_blocks(model, block_sets, s):
    if block_sets == len(prd):
        return pyo.Constraint.Skip
    else:   
        return Full_model.subprobs[block_sets + 1].CCS[s] >=  Full_model.subprobs[block_sets].CCS[s]
        
Full_model.Cons1 = pyo.Constraint(block_sets, s, rule = linking_blocks)

'''
Creating a new objective function for the new model
The objective minimises the cumulative extent of CCS retrofit from all fossil-based sources
'''
TCOST = 0
for i in range(1, numperiods, 1):
    TCOST = TCOST + Full_model.subprobs[i].sum_cost
    
Full_model.obj = pyo.Objective(expr = TCOST, sense = pyo.minimize)

#Using octeract engine solver to solve the energy planning model
opt = SolverFactory('octeract-engine')
results = opt.solve(Full_model)
print(results)
'''
Creating a fuction to publish the results energy planning scenario for a single period

Args:
    source_data = The energy and carbon intensity for [Period Number] 
    period_data = The energy planning data for [Period Number]
    period = Time period involved ('P1' or 'P2' or 'P3')
    
returns:
    the results from variables in the energy planning model, 
    a data table with the energy and emission contribution from each energy source,
    and energy planning pinch diagram
'''

def EP_Results(plant_data, period_data, period):
    model = Full_model.subprobs[period]
    print(' ')
    print('Time period', '=' , period)
    print(' ')
    print('CO2 load limit in', period, '=', model.period_data['Emission_Limit'])
    print(' ')
    print('Revised total CO2 Emission after energy planning in', period, '=', round(model.new_emission(), 2))    
    print(' ')
    print('Minimum NET Deployment in', period, '=', round(model.EC_NET(), 2), 'TWh/y')
    print(' ') 
    print('Total energy cost in', period, '=', round(model.sum_cost(), 2), 'mil RM/y')
    print(' ')
    
    print('Energy deployment in power plant s in', period)
    print(' ')    
    for s in plant_data.keys():    
        print(s, '=', round(model.energy[s](),2))
    print(' ')
    
    print('Selection of power plant s for CCS retrofit in', period)
    print(' ')    
    for s in plant_data.keys():    
        print(s, '=', model.B[s]())
    print(' ')
    
    print('Carbon Intensity of CCS Retrofitted energy sources for power plant s in', period)
    print(' ')    
    for s in plant_data.keys():    
        print(s, '=', round(model.CI_RET[s](), 3), 'TWh/y')
    print(' ')
    
    print('Extent of CCS retrofit on energy sources for power plant s in', period)
    print(' ')    
    for s in plant_data.keys():    
        print(s, '=', round(model.CCS[s](), 2), 'TWh/y')
    print(' ')
    
    print('Net energy from energy sources without CCS retrofit for power plant s in', period)
    print(' ')    
    for s in plant_data.keys():
        print(s, '=', round(model.net_energy[s](), 2), 'TWh/y')
    print(' ')    
    
    print('Net energy from energy sources with CCS retrofit for power plant s in', period)
    print(' ')    
    for s in plant_data.keys():
        print(s, '=', round(model.net_energy_CCS[s](), 2), 'TWh/y')
    print(' ')     
    
    energy_planning = pd.DataFrame()

    for s in plant_data.keys():
        energy_planning.loc['NET', 'Fuel'] = 'EC_NET'        
        energy_planning.loc['COMP', 'Fuel'] = 'COMP'        
        energy_planning.loc[s, 'Fuel'] = plant_data[s]['Fuel']
        energy_planning.loc[s, 'Energy'] = round(model.energy[s](), 2)       
        energy_planning.loc[s, 'CCS Ret'] = round(model.CCS[s](), 2)        
        energy_planning.loc[s, 'Net Energy wo CCS'] = round(model.net_energy[s](), 2)
        energy_planning.loc[s, 'Net Energy w CCS'] = round(model.net_energy_CCS[s](), 2)
        energy_planning.loc[s, 'Net Energy'] = round(model.net_energy[s]() + model.net_energy_CCS[s](), 2)    
        energy_planning.loc['NET', 'Net Energy'] = round(model.EC_NET(),2)
        energy_planning.loc['COMP', 'Net Energy'] = round(model.comp(),2)            
        energy_planning.loc[s, 'Carbon Load'] = round((model.net_energy[s]() * plant_data[s]['CI']) + (model.net_energy_CCS[s]() * model.CI_RET[s]()), 2)
        energy_planning.loc['NET', 'Carbon Load'] = round(model.EC_NET() * model.period_data['EC_NET_CI'], 2)
        energy_planning.loc['COMP', 'Carbon Load'] = round(model.comp() * model.period_data['Comp_CI'], 2)
    
    print('Energy Planning Table for', period)
    print(' ')
    print(energy_planning)
    print(' ')
    
    return    

for i in range (1, numperiods,1):
    EP_Results(plant_data, period_data_dict[i], i)