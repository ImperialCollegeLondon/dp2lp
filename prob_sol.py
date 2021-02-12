# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 11:22:27 2021

@author: sg316
"""

import cplex
import pandas as pd
import json

cpx = cplex.Cplex("opt.lp")
cpx.solve()

objective_value = cpx.solution.get_objective_value()

with open('input_file/input.json') as f:
    data = json.load(f)
 
J = len(data) - 2
T = int(data["T"])
#T = 2
temp = data.keys()
J_list = []
#list of IDs
for j in range(2, J+2):
    J_list.append(list(temp)[j])

P_columns = ["ICD02_AGE1", "ICD02_AGE2", "ICD02_AGE3", "ICD13_AGE1", "ICD13_AGE2",	"ICD13_AGE3", "ICD21_AGE1",	"ICD21_AGE2", "ICD21_AGE3",	"ICD09_AGE1", "ICD09_AGE2",	"ICD09_AGE3",	"ICD18_AGE1",	"ICD18_AGE2",	"ICD18_AGE3",	"ICD19_AGE1",	"ICD19_AGE2",	"ICD19_AGE3",	"ICD07_AGE1",	"ICD07_AGE2",	"ICD07_AGE3",	"ICD12_AGE1",	"ICD12_AGE2",	"ICD12_AGE3", "ICD14_AGE1",	"ICD14_AGE2",	"ICD14_AGE3",	"ICD10_AGE1",	"ICD10_AGE2",	"ICD10_AGE3",	"ICD50_AGE1",	"ICD50_AGE2",	"ICD50_AGE3",	"ICD06_AGE1",	"ICD06_AGE2",	"ICD06_AGE3",	"ICD03_AGE1",	"ICD03_AGE2",	"ICD03_AGE3",	"ICD11_AGE1",	"ICD11_AGE2",	"ICD11_AGE3",	"ICD04_AGE1",	"ICD04_AGE2",	"ICD04_AGE3",	"ICD51_AGE1",	"ICD51_AGE2",	"ICD51_AGE3",	"ICD01_AGE1",	"ICD01_AGE2",	"ICD01_AGE3",	"ICD05_AGE1",	"ICD05_AGE2",	"ICD05_AGE3",	"ICD15_AGE1",	"ICD15_AGE2",	"COVID_AGE1",	"COVID_AGE2",	"COVID_AGE3"]

##writing Mortality, Waiting/Group##
Mortality_Waiting_Group = [[0 for i in range(3)] for j in range(int(len(J_list)/T))]

for j in range(int(len(J_list)/T)):
    name = J_list[T*j]
    Mortality_Waiting_Group[j][0] = name.split("_")[0] + "_"+ name.split("_")[1]
    for k in range(T*j, T*j+52):
        Mortality_Waiting_Group[j][1] += cpx.solution.get_values("sigma_53_" + str(k) + "_7") #mortality
        Mortality_Waiting_Group[j][2] += cpx.solution.get_values("sigma_53_" + str(k) + "_1") #+ cpx.solution.get_values("pi_52_" + str(k) + "_1_0") #waiting 
        
M_W = pd.DataFrame(Mortality_Waiting_Group)  
M_W.columns = ["P", "Mortality", "Waiting"]
writer = pd.ExcelWriter('MW.xlsx')
M_W.to_excel(writer)
writer.save()       

del Mortality_Waiting_Group, M_W

#admission_denials
Admission_Denials_Group_Time = [[0 for i in range(len(P_columns))] for j in range(1,T+2)]

for j in range(int(len(J_list)/T)):
    for t in range(1, T+1):
        Admission_Denials_Group_Time[t-1][j] += cpx.solution.get_values("Z_D_" + str(t) + "_" + str(j))
    
Denials = pd.DataFrame(Admission_Denials_Group_Time)  
Denials.columns = P_columns
writer = pd.ExcelWriter('Admission_Denials.xlsx')
Denials.to_excel(writer)
writer.save()   

del Admission_Denials_Group_Time, Denials

#emergency_admissions   
Admission_E_Group_Time = [[0 for i in range(len(P_columns))] for j in range(1,T+2)]

for j in range(int(len(J_list)/T)):
    for t in range(1, T+1):
        Admission_E_Group_Time[t-1][j] += cpx.solution.get_values("Z_E_" + str(t) + "_" + str(j))
    
Admission_E = pd.DataFrame(Admission_E_Group_Time)  
Admission_E.columns = P_columns
writer = pd.ExcelWriter('Admission_Emergency.xlsx')
Admission_E.to_excel(writer)
writer.save()               

del Admission_E_Group_Time, Admission_E

#elective_admissions 
Admission_N_Group_Time = [[0 for i in range(len(P_columns))] for j in range(1,T+2)]

for j in range(int(len(J_list)/T)):
    for t in range(1, T+1):
        Admission_N_Group_Time[t-1][j] += cpx.solution.get_values("Z_N_" + str(t) + "_" + str(j))
    
Admission_N = pd.DataFrame(Admission_N_Group_Time)  
Admission_N.columns = P_columns
writer = pd.ExcelWriter('Admission_Elective.xlsx')
Admission_N.to_excel(writer)
writer.save()  

del Admission_N_Group_Time, Admission_N
 
#YLL
YLL_t_Group = [[0 for i in range(len(P_columns))] for j in range(1,T+2)]
for j in range(int(len(J_list)/T)):
    for t in range(1, T+1):
        YLL_t_Group[t-1][j] = cpx.solution.get_values("Y_" + str(t) + "_" + str(j))

YLL = pd.DataFrame(YLL_t_Group)
YLL.columns = P_columns
writer = pd.ExcelWriter('YLL.xlsx')
YLL.to_excel(writer)
writer.save()  
del YLL, YLL_t_Group

#Resource Utilisation
G_t_Group = [[0 for i in range(len(P_columns))] for j in range(1,T+2)]
C_t_Group = [[0 for i in range(len(P_columns))] for j in range(1,T+2)]
for j in range(int(len(J_list)/T)):
    for t in range(1, T+1):
        G_t_Group[t-1][j] = cpx.solution.get_values("G_" + str(t) + "_" + str(j))
        C_t_Group[t-1][j] = cpx.solution.get_values("C_" + str(t) + "_" + str(j))

G_beds = pd.DataFrame(G_t_Group)
C_beds = pd.DataFrame(C_t_Group)
G_beds.columns = P_columns
C_beds.columns = P_columns
writer = pd.ExcelWriter('RU.xlsx')
G_beds.to_excel(writer, 'GBeds')
C_beds.to_excel(writer, 'CBeds')
writer.save()  

del G_t_Group, C_t_Group, G_beds, C_beds

#G*admissions
G_Star_t_Group = [[0 for i in range(len(P_columns))] for j in range(1,T+1)]
for j in range(int(len(J_list)/T)):
    for t in range(1, T+1):
        G_Star_t_Group[t-1][j] = cpx.solution.get_values("G_Star_" + str(t) + "_" + str(j))

G_Star = pd.DataFrame(G_Star_t_Group)
G_Star.columns = P_columns
writer = pd.ExcelWriter('G_Star.xlsx')
G_Star.to_excel(writer)
writer.save()  

del G_Star, G_Star_t_Group

##CC_E, CC_N, G_Star_N, G_Star_E, G_N, G_E
G_Star_N_t_Group = [[0 for i in range(len(P_columns))] for j in range(1,T+1)]
G_Star_E_t_Group = [[0 for i in range(len(P_columns))] for j in range(1,T+1)]
CC_N_t_Group = [[0 for i in range(len(P_columns))] for j in range(1,T+1)]
CC_E_t_Group = [[0 for i in range(len(P_columns))] for j in range(1,T+1)]
G_N_t_Group = [[0 for i in range(len(P_columns))] for j in range(1,T+1)]
G_E_t_Group = [[0 for i in range(len(P_columns))] for j in range(1,T+1)]
for j in range(int(len(J_list)/T)):
    for t in range(1, T+1):
        G_Star_N_t_Group[t-1][j] = cpx.solution.get_values("G_Star_N_" + str(t) + "_" + str(j))
        G_Star_E_t_Group[t-1][j] = cpx.solution.get_values("G_Star_E_" + str(t) + "_" + str(j))
        CC_N_t_Group[t-1][j] = cpx.solution.get_values("CC_N_" + str(t) + "_" + str(j))
        CC_E_t_Group[t-1][j] = cpx.solution.get_values("CC_E_" + str(t) + "_" + str(j))
        G_N_t_Group[t-1][j] = cpx.solution.get_values("G_N_" + str(t) + "_" + str(j))
        G_E_t_Group[t-1][j] = cpx.solution.get_values("G_E_" + str(t) + "_" + str(j))

G_Star_N = pd.DataFrame(G_Star_N_t_Group)
G_Star_N.columns = P_columns
G_Star_E = pd.DataFrame(G_Star_E_t_Group)
G_Star_E.columns = P_columns
C_N = pd.DataFrame(CC_N_t_Group)
C_N.columns = P_columns
C_E = pd.DataFrame(CC_E_t_Group)
C_E.columns = P_columns
G_N = pd.DataFrame(G_N_t_Group)
G_N.columns = P_columns
G_E = pd.DataFrame(G_E_t_Group)
G_E.columns = P_columns

writer = pd.ExcelWriter('G_Star_CC.xlsx')
G_Star_N.to_excel(writer, 'G_Star_N')
G_Star_E.to_excel(writer, 'G_Star_E')
C_N.to_excel(writer, 'C_N')
C_E.to_excel(writer, 'C_E')
G_N.to_excel(writer, 'G_N')
G_E.to_excel(writer, 'G_E')
writer.save()  


