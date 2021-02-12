#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 18:23:37 2021

@author: shubhechyya
"""

import json
import xlrd
import numpy as np

##read data from the excel file
wb = xlrd.open_workbook('input_file/User_Input.xlsx')
num_sheets = wb.nsheets
dict_temp = {}

#read global values
sheet_global = wb.sheet_by_index(0)
dict_temp["T"] = sheet_global.cell_value(0, 1)
T = int(sheet_global.cell_value(0, 1))
dict_temp["b"] = {}

#resources: GBeds, CBeds, GSDoctor, GJDoctor, GNurse, CSDoctor, CJDoctor, CNurse
for t in range(1, T+1):
    dict_temp["b"][str(t)] = []
    for r in range(2):
        dict_temp["b"][str(t)].append(sheet_global.cell_value(3+r, 1))
    for r in range(3, 9):
        dict_temp["b"][str(t)].append(sheet_global.cell_value(5+r, 2)*100)

resources = ["GBeds", "CBeds", "GSDoctor", "GJDoctor", "GNurse", "CSDoctor", "CJDoctor", "CNurse"]

#read values for each ICD
for num in range(1, num_sheets):
    sheet = wb.sheet_by_index(num)
    ID = sheet.cell_value(0,1)
###change this to if total inflow + stock == 0, then skip over this iterate
    if (ID == "ICD15_AGE3"):
        continue
    print(ID)
    for t in range(1, T+1):
        name = str(ID) + "_" + str(t)
        T0 = t
        dict_temp[name] = {"STATES": ["Dormant", "N", "E", "G, N", "C, N", "G, E", "C, E", "D", "H"]} 
        
        #reading in "n"
        if(t == 1):
            dict_temp[name]["n"] = sheet.cell_value(17,1) + sheet.cell_value(18,1) + sheet.cell_value(2,1) + sheet.cell_value(5,1) + sheet.cell_value(5,2) + sheet.cell_value(6,1) + sheet.cell_value(6,2)
        else:
            dict_temp[name]["n"] = sheet.cell_value(17,t) + sheet.cell_value(18,t)
                         
        #reading in "q"
        dict_temp[name]["q"] = [0 for s in range(len(dict_temp[name]["STATES"]))]
        if(t == 1):
            dict_temp[name]["q"][1] = (sheet.cell_value(18,1) + sheet.cell_value(2,1))/dict_temp[name]["n"]
            dict_temp[name]["q"][2] = sheet.cell_value(17,1)/dict_temp[name]["n"]
            dict_temp[name]["q"][3] = sheet.cell_value(6,1)/dict_temp[name]["n"]
            dict_temp[name]["q"][4] = sheet.cell_value(6,2)/dict_temp[name]["n"]
            dict_temp[name]["q"][5] = sheet.cell_value(5,1)/dict_temp[name]["n"]
            dict_temp[name]["q"][6] = sheet.cell_value(5,2)/dict_temp[name]["n"]
            
        else:
            dict_temp[name]["q"][0] = 1
        
        dict_temp[name]["ACTIONS"] = ["DoNot","Admit", "AdmitG*","MoveG", "MoveC", "MoveG*"]
        dict_temp[name]["ADM_ACTIONS"] = {"Dormant": ["DoNot"], "N": ["DoNot", "Admit", "AdmitG*"], "E": ["DoNot", "Admit", "AdmitG*"], "G, E": ["MoveG"], "C, E": ["MoveC", "MoveG*"], "G, N": ["MoveG"], "C, N": ["MoveC", "MoveG*"], "D": ["DoNot"], "H":["DoNot"]}
        
        n_states = len(dict_temp[name]["STATES"])
        n_actions = len(dict_temp[name]["ACTIONS"])
        #reading in TP
        dict_temp[name]["TP"] = []
        dict_TP = {}
        dict_temp[name]["TP"].append(dict_TP)
        for t1 in range(1, T+1):
            dict_TP[str(t1)] = []
            dict_TP_state = {}
            dict_TP[str(t1)].append(dict_TP_state)
            for s in dict_temp[name]["STATES"]:
                dict_TP_state[str(s)] = [[0 for i in range(n_states)] for j in range (n_actions)]
            if (t1 < T0 - 1):   
                dict_TP_state["Dormant"][dict_temp[name]["ACTIONS"].index("DoNot")][dict_temp[name]["STATES"].index("Dormant")] = 1
            else:
                dict_TP_state["Dormant"][dict_temp[name]["ACTIONS"].index("DoNot")][dict_temp[name]["STATES"].index("N")] = sheet.cell_value(18,t)/(sheet.cell_value(17,t)+sheet.cell_value(18,t)) 
                dict_TP_state["Dormant"][dict_temp[name]["ACTIONS"].index("DoNot")][dict_temp[name]["STATES"].index("E")] = sheet.cell_value(17,t)/(sheet.cell_value(17,t)+sheet.cell_value(18,t)) 
                
                dict_TP_state["N"][dict_temp[name]["ACTIONS"].index("Admit")][dict_temp[name]["STATES"].index("G, N")] = (1 - sheet.cell_value(22,t1))*sheet.cell_value(34,1) + sheet.cell_value(22,t1)*sheet.cell_value(36,1)
                dict_TP_state["N"][dict_temp[name]["ACTIONS"].index("Admit")][dict_temp[name]["STATES"].index("C, N")] = (1 - sheet.cell_value(22,t1))*sheet.cell_value(34,2) + sheet.cell_value(22,t1)*sheet.cell_value(36,2)
                dict_TP_state["N"][dict_temp[name]["ACTIONS"].index("Admit")][dict_temp[name]["STATES"].index("D")] = (1 - sheet.cell_value(22,t1))*sheet.cell_value(34,3) + sheet.cell_value(22,t1)*sheet.cell_value(36,3)
                dict_TP_state["N"][dict_temp[name]["ACTIONS"].index("Admit")][dict_temp[name]["STATES"].index("H")] = (1 - sheet.cell_value(22,t1))*sheet.cell_value(34,4) + sheet.cell_value(22,t1)*sheet.cell_value(36,4)
                
                dict_TP_state["N"][dict_temp[name]["ACTIONS"].index("AdmitG*")][dict_temp[name]["STATES"].index("G, N")] = sheet.cell_value(35,1) 
                dict_TP_state["N"][dict_temp[name]["ACTIONS"].index("AdmitG*")][dict_temp[name]["STATES"].index("C, N")] = sheet.cell_value(35,2) 
                dict_TP_state["N"][dict_temp[name]["ACTIONS"].index("AdmitG*")][dict_temp[name]["STATES"].index("D")] = sheet.cell_value(35,3) 
                dict_TP_state["N"][dict_temp[name]["ACTIONS"].index("AdmitG*")][dict_temp[name]["STATES"].index("H")] = sheet.cell_value(35,4) 
                
                dict_TP_state["N"][dict_temp[name]["ACTIONS"].index("DoNot")][dict_temp[name]["STATES"].index("N")] = 1 - sheet.cell_value(8,1)
                dict_TP_state["N"][dict_temp[name]["ACTIONS"].index("DoNot")][dict_temp[name]["STATES"].index("E")] = sheet.cell_value(8,1) 
                
                dict_TP_state["E"][dict_temp[name]["ACTIONS"].index("Admit")][dict_temp[name]["STATES"].index("G, E")] = (1 - sheet.cell_value(21,t1))*sheet.cell_value(29,1) + sheet.cell_value(21,t1)*sheet.cell_value(31,1)
                dict_TP_state["E"][dict_temp[name]["ACTIONS"].index("Admit")][dict_temp[name]["STATES"].index("C, E")] = (1 - sheet.cell_value(21,t1))*sheet.cell_value(29,2) + sheet.cell_value(21,t1)*sheet.cell_value(31,2)
                dict_TP_state["E"][dict_temp[name]["ACTIONS"].index("Admit")][dict_temp[name]["STATES"].index("D")] = (1 - sheet.cell_value(21,t1))*sheet.cell_value(29,3) + sheet.cell_value(21,t1)*sheet.cell_value(31,3)
                dict_TP_state["E"][dict_temp[name]["ACTIONS"].index("Admit")][dict_temp[name]["STATES"].index("H")] = (1 - sheet.cell_value(21,t1))*sheet.cell_value(29,4) + sheet.cell_value(21,t1)*sheet.cell_value(31,4)
                
                dict_TP_state["E"][dict_temp[name]["ACTIONS"].index("AdmitG*")][dict_temp[name]["STATES"].index("G, E")] = sheet.cell_value(30,1) 
                dict_TP_state["E"][dict_temp[name]["ACTIONS"].index("AdmitG*")][dict_temp[name]["STATES"].index("C, E")] = sheet.cell_value(30,2)                 
                dict_TP_state["E"][dict_temp[name]["ACTIONS"].index("AdmitG*")][dict_temp[name]["STATES"].index("D")] = sheet.cell_value(30,3) 
                dict_TP_state["E"][dict_temp[name]["ACTIONS"].index("AdmitG*")][dict_temp[name]["STATES"].index("H")] = sheet.cell_value(30,4) 
                
                dict_TP_state["E"][dict_temp[name]["ACTIONS"].index("DoNot")][dict_temp[name]["STATES"].index("D")] = 1 
                
                dict_TP_state["G, N"][dict_temp[name]["ACTIONS"].index("MoveG")][dict_temp[name]["STATES"].index("G, N")] = sheet.cell_value(34,1)
                dict_TP_state["G, N"][dict_temp[name]["ACTIONS"].index("MoveG")][dict_temp[name]["STATES"].index("C, N")] = sheet.cell_value(34,2)
                dict_TP_state["G, N"][dict_temp[name]["ACTIONS"].index("MoveG")][dict_temp[name]["STATES"].index("D")] = sheet.cell_value(34,3)
                dict_TP_state["G, N"][dict_temp[name]["ACTIONS"].index("MoveG")][dict_temp[name]["STATES"].index("H")] = sheet.cell_value(34,4) 
                
                dict_TP_state["C, N"][dict_temp[name]["ACTIONS"].index("MoveG*")][dict_temp[name]["STATES"].index("G, N")] = sheet.cell_value(35,1) 
                dict_TP_state["C, N"][dict_temp[name]["ACTIONS"].index("MoveG*")][dict_temp[name]["STATES"].index("C, N")] = sheet.cell_value(35,2)  
                dict_TP_state["C, N"][dict_temp[name]["ACTIONS"].index("MoveG*")][dict_temp[name]["STATES"].index("D")] = sheet.cell_value(35,3)  
                dict_TP_state["C, N"][dict_temp[name]["ACTIONS"].index("MoveG*")][dict_temp[name]["STATES"].index("H")] = sheet.cell_value(35,4)  
                
                dict_TP_state["C, N"][dict_temp[name]["ACTIONS"].index("MoveC")][dict_temp[name]["STATES"].index("G, N")] = sheet.cell_value(36,1)   
                dict_TP_state["C, N"][dict_temp[name]["ACTIONS"].index("MoveC")][dict_temp[name]["STATES"].index("C, N")] = sheet.cell_value(36,2) 
                dict_TP_state["C, N"][dict_temp[name]["ACTIONS"].index("MoveC")][dict_temp[name]["STATES"].index("D")] = sheet.cell_value(36,3) 
                dict_TP_state["C, N"][dict_temp[name]["ACTIONS"].index("MoveC")][dict_temp[name]["STATES"].index("H")] = sheet.cell_value(36,4) 
                
                dict_TP_state["G, E"][dict_temp[name]["ACTIONS"].index("MoveG")][dict_temp[name]["STATES"].index("G, E")] = sheet.cell_value(29,1) 
                dict_TP_state["G, E"][dict_temp[name]["ACTIONS"].index("MoveG")][dict_temp[name]["STATES"].index("C, E")] = sheet.cell_value(29,2) 
                dict_TP_state["G, E"][dict_temp[name]["ACTIONS"].index("MoveG")][dict_temp[name]["STATES"].index("D")] = sheet.cell_value(29,3) 
                dict_TP_state["G, E"][dict_temp[name]["ACTIONS"].index("MoveG")][dict_temp[name]["STATES"].index("H")] = sheet.cell_value(29,4)  
                
                dict_TP_state["C, E"][dict_temp[name]["ACTIONS"].index("MoveG*")][dict_temp[name]["STATES"].index("G, E")] = sheet.cell_value(30,1) 
                dict_TP_state["C, E"][dict_temp[name]["ACTIONS"].index("MoveG*")][dict_temp[name]["STATES"].index("C, E")] = sheet.cell_value(30,2) 
                dict_TP_state["C, E"][dict_temp[name]["ACTIONS"].index("MoveG*")][dict_temp[name]["STATES"].index("D")] = sheet.cell_value(30,3) 
                dict_TP_state["C, E"][dict_temp[name]["ACTIONS"].index("MoveG*")][dict_temp[name]["STATES"].index("H")] = sheet.cell_value(30,4) 
                
                dict_TP_state["C, E"][dict_temp[name]["ACTIONS"].index("MoveC")][dict_temp[name]["STATES"].index("G, E")] = sheet.cell_value(31,1)  
                dict_TP_state["C, E"][dict_temp[name]["ACTIONS"].index("MoveC")][dict_temp[name]["STATES"].index("C, E")] = sheet.cell_value(31,2)  
                dict_TP_state["C, E"][dict_temp[name]["ACTIONS"].index("MoveC")][dict_temp[name]["STATES"].index("D")] = sheet.cell_value(31,3)  
                dict_TP_state["C, E"][dict_temp[name]["ACTIONS"].index("MoveC")][dict_temp[name]["STATES"].index("H")] = sheet.cell_value(31,4) 
                
                dict_TP_state["H"][dict_temp[name]["ACTIONS"].index("DoNot")][dict_temp[name]["STATES"].index("H")] = 1 
                dict_TP_state["D"][dict_temp[name]["ACTIONS"].index("DoNot")][dict_temp[name]["STATES"].index("D")] = 1

        #reading in "r"YLL  
        dict_temp[name]["r"] = []
        dict_r = {}
        dict_temp[name]["r"].append(dict_r)
        for t1 in range(1, T+1):
            dict_r[str(t1)] = []
            dict_r_state = {}
            dict_r[str(t1)].append(dict_r_state)
            for s in dict_temp[name]["STATES"]:
                dict_r_state[str(s)] = [0 for i in range(n_actions)]
            dict_r_state["E"][dict_temp[name]["ACTIONS"].index("DoNot")] = -sheet.cell_value(10,1)
            dict_r_state["E"][dict_temp[name]["ACTIONS"].index("Admit")] = -sheet.cell_value(10,1)*((1 - sheet.cell_value(21,t1))*sheet.cell_value(29,3) + sheet.cell_value(21,t1)*sheet.cell_value(31,3))
            dict_r_state["E"][dict_temp[name]["ACTIONS"].index("AdmitG*")] = -sheet.cell_value(10,1)*sheet.cell_value(30,3)
            dict_r_state["N"][dict_temp[name]["ACTIONS"].index("Admit")] = -sheet.cell_value(10,1)*((1 - sheet.cell_value(22,t1))*sheet.cell_value(34,3) + sheet.cell_value(22,t1)*sheet.cell_value(36,3))
            dict_r_state["N"][dict_temp[name]["ACTIONS"].index("AdmitG*")] = -sheet.cell_value(10,1)*sheet.cell_value(35,3)
            dict_r_state["G, N"][dict_temp[name]["ACTIONS"].index("MoveG")] = -sheet.cell_value(10,1)*sheet.cell_value(34,3)
            dict_r_state["C, N"][dict_temp[name]["ACTIONS"].index("MoveG*")] = -sheet.cell_value(10,1)*sheet.cell_value(35,3)  
            dict_r_state["C, N"][dict_temp[name]["ACTIONS"].index("MoveC")] = -sheet.cell_value(10,1)*sheet.cell_value(36,3) 
            dict_r_state["G, E"][dict_temp[name]["ACTIONS"].index("MoveG")] = -sheet.cell_value(10,1)*sheet.cell_value(29,3) 
            dict_r_state["C, E"][dict_temp[name]["ACTIONS"].index("MoveG*")] = -sheet.cell_value(10,1)*sheet.cell_value(30,3) 
            dict_r_state["C, E"][dict_temp[name]["ACTIONS"].index("MoveC")] = -sheet.cell_value(10,1)*sheet.cell_value(31,3)  
        
        #reading in "c" #resource utilization
        dict_temp[name]["c"] = []
        dict_c = {}
        dict_temp[name]["c"].append(dict_c)
        for t1 in range(1, T+1):
            dict_c[str(t1)] = []
            dict_c_t = {}
            dict_c[str(t1)].append(dict_c_t)
            for r in range(1, len(resources)+1):
                dict_c_t[str(r)] = []  
                dict_c_r = {} 
                dict_c_t[str(r)].append(dict_c_r)
                for s in dict_temp[name]["STATES"]:
                    dict_c_r[str(s)] = [0 for i in range(n_actions)]
        
            dict_c_t["1"][0]["G, N"][dict_temp[name]["ACTIONS"].index("MoveG")] = np.sum([1*sheet.cell_value(34,i) for i in range(1,3)]) + np.sum([sheet.cell_value(26,1)*sheet.cell_value(34,i) for i in range(3,5)])
            dict_c_t["1"][0]["C, N"][dict_temp[name]["ACTIONS"].index("MoveG*")] = np.sum([1*sheet.cell_value(35,i) for i in range(1,3)]) + np.sum([sheet.cell_value(26,1)*sheet.cell_value(35,i) for i in range(3,5)])
            dict_c_t["1"][0]["G, E"][dict_temp[name]["ACTIONS"].index("MoveG")] = np.sum([1*sheet.cell_value(29,i) for i in range(1,3)])+ np.sum([sheet.cell_value(25,1)*sheet.cell_value(29,i) for i in range(3,5)])
            dict_c_t["1"][0]["C, E"][dict_temp[name]["ACTIONS"].index("MoveG*")] = np.sum([1*sheet.cell_value(30,i) for i in range(1,3)])+ np.sum([sheet.cell_value(25,1)*sheet.cell_value(30,i) for i in range(3,5)])
            dict_c_t["1"][0]["N"][dict_temp[name]["ACTIONS"].index("Admit")] = (1 - sheet.cell_value(22,t1))*(np.sum([1*sheet.cell_value(34,i) for i in range(1,3)])+ np.sum([sheet.cell_value(26,1)*sheet.cell_value(34,i) for i in range(3,5)]))
            dict_c_t["1"][0]["N"][dict_temp[name]["ACTIONS"].index("AdmitG*")] = np.sum([1*sheet.cell_value(35,i) for i in range(1,3)])+ np.sum([sheet.cell_value(26,1)*sheet.cell_value(35,i) for i in range(3,5)])
            dict_c_t["1"][0]["E"][dict_temp[name]["ACTIONS"].index("Admit")] = (1 - sheet.cell_value(21,t1))*(np.sum([1*sheet.cell_value(29,i) for i in range(1,3)])+ np.sum([sheet.cell_value(25,1)*sheet.cell_value(29,i) for i in range(3,5)]))
            dict_c_t["1"][0]["E"][dict_temp[name]["ACTIONS"].index("AdmitG*")] = np.sum([1*sheet.cell_value(30,i) for i in range(1,3)])+ np.sum([sheet.cell_value(25,1)*sheet.cell_value(30,i) for i in range(3,5)])
            
            G_staff = np.arange(3,6)
            for g in G_staff:
                dict_c_t[str(g)][0]["G, N"][dict_temp[name]["ACTIONS"].index("MoveG")] = dict_c_t["1"][0]["G, N"][dict_temp[name]["ACTIONS"].index("MoveG")]/sheet_global.cell_value(13+g,1) 
                dict_c_t[str(g)][0]["C, N"][dict_temp[name]["ACTIONS"].index("MoveG*")] = dict_c_t["1"][0]["C, N"][dict_temp[name]["ACTIONS"].index("MoveG*")]/sheet_global.cell_value(13+g,1) 
                dict_c_t[str(g)][0]["G, E"][dict_temp[name]["ACTIONS"].index("MoveG")] = dict_c_t["1"][0]["G, E"][dict_temp[name]["ACTIONS"].index("MoveG")]/sheet_global.cell_value(13+g,1)
                dict_c_t[str(g)][0]["C, E"][dict_temp[name]["ACTIONS"].index("MoveG*")] = dict_c_t["1"][0]["C, E"][dict_temp[name]["ACTIONS"].index("MoveG*")]/sheet_global.cell_value(13+g,1)
                dict_c_t[str(g)][0]["N"][dict_temp[name]["ACTIONS"].index("Admit")] = dict_c_t["1"][0]["N"][dict_temp[name]["ACTIONS"].index("Admit")]/sheet_global.cell_value(13+g,1)
                dict_c_t[str(g)][0]["N"][dict_temp[name]["ACTIONS"].index("AdmitG*")] = dict_c_t["1"][0]["N"][dict_temp[name]["ACTIONS"].index("AdmitG*")]/sheet_global.cell_value(13+g,1)
                dict_c_t[str(g)][0]["E"][dict_temp[name]["ACTIONS"].index("Admit")] = dict_c_t["1"][0]["E"][dict_temp[name]["ACTIONS"].index("Admit")]/sheet_global.cell_value(13+g,1)
                dict_c_t[str(g)][0]["E"][dict_temp[name]["ACTIONS"].index("AdmitG*")] = dict_c_t["1"][0]["E"][dict_temp[name]["ACTIONS"].index("AdmitG*")]/sheet_global.cell_value(13+g,1)
                            
            dict_c_t["2"][0]["C, N"][dict_temp[name]["ACTIONS"].index("MoveC")] = np.sum([1*sheet.cell_value(36,i) for i in range(1,3)])+ np.sum([sheet.cell_value(26,2)*sheet.cell_value(36,i) for i in range(3,5)])
            dict_c_t["2"][0]["C, E"][dict_temp[name]["ACTIONS"].index("MoveC")] = np.sum([1*sheet.cell_value(31,i) for i in range(1,3)])+ np.sum([sheet.cell_value(25,2)*sheet.cell_value(31,i) for i in range(3,5)])
            dict_c_t["2"][0]["N"][dict_temp[name]["ACTIONS"].index("Admit")] = sheet.cell_value(22,t1)*(np.sum([1*sheet.cell_value(36,i) for i in range(1,3)])+ np.sum([sheet.cell_value(26,2)*sheet.cell_value(36,i) for i in range(3,5)]))
            dict_c_t["2"][0]["E"][dict_temp[name]["ACTIONS"].index("Admit")] = sheet.cell_value(21,t1)*(np.sum([1*sheet.cell_value(31,i) for i in range(1,3)])+ np.sum([sheet.cell_value(25,2)*sheet.cell_value(31,i) for i in range(3,5)]))
            
            C_staff = np.arange(6,9)
            for g in C_staff:
                dict_c_t[str(g)][0]["C, N"][dict_temp[name]["ACTIONS"].index("MoveC")] = dict_c_t["2"][0]["C, N"][dict_temp[name]["ACTIONS"].index("MoveC")]/sheet_global.cell_value(13+g,1)
                dict_c_t[str(g)][0]["C, E"][dict_temp[name]["ACTIONS"].index("MoveC")] = dict_c_t["2"][0]["C, E"][dict_temp[name]["ACTIONS"].index("MoveC")]/sheet_global.cell_value(13+g,1)
                dict_c_t[str(g)][0]["N"][dict_temp[name]["ACTIONS"].index("Admit")] = dict_c_t["2"][0]["N"][dict_temp[name]["ACTIONS"].index("Admit")]/sheet_global.cell_value(13+g,1)
                dict_c_t[str(g)][0]["E"][dict_temp[name]["ACTIONS"].index("Admit")] = dict_c_t["2"][0]["E"][dict_temp[name]["ACTIONS"].index("Admit")]/sheet_global.cell_value(13+g,1)
                

with open("input_file/input.json", "w") as outfile: 
    json.dump(dict_temp, outfile)
