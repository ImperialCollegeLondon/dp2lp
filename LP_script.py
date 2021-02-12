#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 09:55:14 2021

@author: shubhechyya
"""
import json
import os

with open('input_file/input.json') as f:
    data = json.load(f)
 
J = len(data) - 2
T = int(data["T"])
#T = 10
temp = data.keys()
J_list = []
#list of IDs
for j in range(2, J+2):
    J_list.append(list(temp)[j])


f = open("opt.txt", "w")
f.write("Maximize \n")
f.write("obj:\t")
temp_obj = ""
for t in range(1, T+1):
    for j in range(len(J_list)):
        for s in range(len(data[J_list[j]]['STATES'])):
            s_var = data[J_list[j]]['STATES'][s]
            for a in range(len(data[J_list[j]]['ACTIONS'])):
                r = abs(data[J_list[j]]["r"][0][str(t)][0][s_var][a])           
                temp_obj += " -" + str(r) + "pi_"+ str(t)+ "_" + str(j) + "_"+ str(s) + "_" + str(a)  

temp_obj += "\n"
f.write(temp_obj)
f.write("Subject To \n")
constr_num = 1

for j in range(len(J_list)):
    for s in range(len(data[J_list[j]]['STATES'])):
        f.write("c"+str(constr_num)+":\t")
        constr_num += 1
        temp_constr = "sigma_1_" + str(j) + "_" + str(s) + " =" +  str(data[J_list[j]]["n"]*data[J_list[j]]["q"][s])
        f.write(temp_constr + "\n")
        
for j in range(len(J_list)):
    for s in range(len(data[J_list[j]]['STATES'])):
        for t in range(1,T+1):
            f.write("c"+str(constr_num)+":\t")
            constr_num += 1
            constr_temp_LHS = "sigma_"+ str(t + 1) + "_" + str(j) + "_" + str(s)
            constr_temp_RHS = ""
            for s_sum in range(len(data[J_list[j]]['STATES'])):
                s_sum_var = data[J_list[j]]['STATES'][s_sum] 
                for a_sum in range(len(data[J_list[j]]['ACTIONS'])):
                    r = data[J_list[j]]["TP"][0][str(t)][0][s_sum_var][a_sum][s]
                    constr_temp_RHS += str(r) + "pi_" + str(t) + "_" + str(j) + "_" + str(s_sum) + "_" + str(a_sum) + "+"
            constr_temp =  constr_temp_RHS[:-1] + "-" + constr_temp_LHS + "= 0 \n"
            f.write(constr_temp)   
            
for j in range(len(J_list)):
    for s in range(len(data[J_list[j]]['STATES'])):
        s_var = data[J_list[j]]['STATES'][s]
        for t in range(1,T+1):
            f.write("c"+str(constr_num)+":\t")
            constr_num += 1
            constr_temp_RHS = "sigma_" + str(t) + "_" + str(j) + "_" + str(s)
            constr_temp_LHS = ""
            for a_sum in range(len(data[J_list[j]]['ACTIONS'])):
                constr_temp_LHS += "pi_" + str(t) + "_" + str(j) + "_" + str(s) + "_" + str(a_sum) + "+"       
            constr_temp = constr_temp_LHS[:-1] + "-" + constr_temp_RHS + "= 0 \n"
            f.write(constr_temp) 

for t in range(1,T+1):
    for l in range(len(data["b"][str(t)])):   
        f.write("c"+str(constr_num)+":\t")
        constr_num += 1
        constr_temp_RHS = "<=" + str(data["b"][str(t)][l]) + "\n"
        constr_temp_LHS = ""
        for j in range(len(J_list)):
            for s in range(len(data[J_list[j]]['STATES'])):
                s_var = data[J_list[j]]['STATES'][s]
                for a in range(len(data[J_list[j]]['ACTIONS'])):
                    constr_temp_LHS += str(data[J_list[j]]["c"][0][str(t)][0][str(l+1)][0][s_var][a]) + "pi_"+ str(t) + "_" + str(j) + "_" + str(s) + "_" + str(a) + "+"
        constr_temp_LHS = constr_temp_LHS[:-1]
        constr_temp = constr_temp_LHS + constr_temp_RHS 
        f.write(constr_temp) 

for t in range(1,T+1):
    for j in range(len(J_list)):
        for s in range(len(data[J_list[j]]['STATES'])):
            s_var = data[J_list[j]]['STATES'][s]
            a_not = set(data[J_list[j]]['ADM_ACTIONS'][s_var])
            for a in range(len(data[J_list[j]]['ACTIONS'])):            
                if (data[J_list[j]]['ACTIONS'][a] not in a_not):
                    f.write("c"+str(constr_num)+":\t")
                    constr_num += 1
                    constr_temp = "pi_" + str(t) + "_" + str(j) + "_" + str(s) + "_" + str(a) + " = 0\n"
                    f.write(constr_temp) 
            
###resource utilization##
for j in range(int(len(J_list)/T)):
    for t in range(1, T+1):
        constr_temp_LHS_G_beds = ""
        constr_temp_LHS_C_beds = ""
        for k in range(T*j, T*(j+1)):
            for s in range(len(data[J_list[k]]['STATES'])):
                s_var = data[J_list[k]]['STATES'][s]
                for a in range(len(data[J_list[k]]['ACTIONS'])):
                    constr_temp_LHS_G_beds += str(data[J_list[k]]["c"][0][str(t)][0]["1"][0][s_var][a]) + "pi_"+ str(t) + "_" + str(k) + "_" + str(s) + "_" + str(a) + "+"
                    constr_temp_LHS_C_beds += str(data[J_list[k]]["c"][0][str(t)][0]["2"][0][s_var][a]) + "pi_"+ str(t) + "_" + str(k) + "_" + str(s) + "_" + str(a) + "+"
    
        constr_temp_LHS_G_beds = constr_temp_LHS_G_beds[:-1]
        constr_temp_LHS_C_beds = constr_temp_LHS_C_beds[:-1]
        G_beds = constr_temp_LHS_G_beds + "- G_"+ str(t)+ "_" + str(j) + "= 0 \n"
        f.write("c"+str(constr_num)+":\t")
        constr_num += 1
        f.write(G_beds)
        C_beds = constr_temp_LHS_C_beds + "- C_"+ str(t)+ "_" + str(j) + "= 0 \n"
        f.write("c"+str(constr_num)+":\t")
        constr_num += 1
        f.write(C_beds)

###YLL##
for j in range(int(len(J_list)/T)):
    for t in range(1, T+1):
        constr_temp_LHS_YLL = ""
        for k in range(T*j, T*(j+1)):
            for s in range(len(data[J_list[k]]['STATES'])):
                s_var = data[J_list[k]]['STATES'][s]
                for a in range(len(data[J_list[k]]['ACTIONS'])):
                    r = abs(data[J_list[k]]["r"][0][str(t)][0][s_var][a]) 
                    constr_temp_LHS_YLL += str(r) + "pi_"+ str(t) + "_" + str(k) + "_" + str(s) + "_" + str(a) + "+"
                    
        constr_temp_LHS_YLL = constr_temp_LHS_YLL[:-1]
        constr_YLL = constr_temp_LHS_YLL + "- Y_"+ str(t)+ "_" + str(j) + "= 0 \n"
        f.write("c"+str(constr_num)+":\t")
        constr_num += 1
        f.write(constr_YLL)

### G_Star##
for j in range(int(len(J_list)/T)):
    for t in range(1, T+1):
        constr_temp_LHS_G_Star = ""
        for k in range(T*j, T*(j+1)):
            constr_temp_LHS_G_Star += str(data[J_list[k]]["c"][0][str(t)][0]["1"][0]["N"][2]) + "pi_" + str(t) + "_" + str(k) + "_1_2 +" + str(data[J_list[k]]["c"][0][str(t)][0]["1"][0]["E"][2]) + "pi_" + str(t) + "_" + str(k) + "_2_2 +" + str(data[J_list[k]]["c"][0][str(t)][0]["1"][0]["C, N"][5]) +"pi_" + str(t) + "_" + str(k) + "_4_5 +" + str(data[J_list[k]]["c"][0][str(t)][0]["1"][0]["C, E"][5]) +"pi_" + str(t) + "_" + str(k) + "_6_5 +"
                    
        constr_temp_LHS_G_Star = constr_temp_LHS_G_Star[:-1]
        constr_G_Star = constr_temp_LHS_G_Star + "- G_Star_"+ str(t)+ "_" + str(j) + "= 0 \n"
        f.write("c"+str(constr_num)+":\t")
        constr_num += 1
        f.write(constr_G_Star)
 
###Z_N ## Z_D #admission denials ##Z_E
for j in range(int(len(J_list)/T)):
    for t in range(1, T+1):
        constr_temp_LHS_Z_N = ""
        constr_temp_LHS_Z_D = ""
        constr_temp_LHS_Z_E = ""
        for k in range(T*j, T*(j+1)):
            constr_temp_LHS_Z_N += "pi_" + str(t) + "_" + str(k) + "_1_1 +" + "pi_" + str(t) + "_" + str(k) + "_1_2 +"
            constr_temp_LHS_Z_D += "pi_" + str(t) + "_" + str(k) + "_2_0 +"        
            constr_temp_LHS_Z_E += "pi_" + str(t) + "_" + str(k) + "_2_1 + " + "pi_" + str(t) + "_" + str(k) + "_2_2 +"
            
        constr_temp_LHS_Z_N = constr_temp_LHS_Z_N[:-1]
        constr_Z_N = constr_temp_LHS_Z_N + "- Z_N_"+ str(t)+ "_" + str(j) + "= 0 \n"
        f.write("c"+str(constr_num)+":\t")
        constr_num += 1
        f.write(constr_Z_N)
        
        constr_temp_LHS_Z_D = constr_temp_LHS_Z_D[:-1]
        constr_Z_D = constr_temp_LHS_Z_D + "- Z_D_"+ str(t)+ "_" + str(j) + "= 0 \n"
        f.write("c"+str(constr_num)+":\t")
        constr_num += 1
        f.write(constr_Z_D)
        
        constr_temp_LHS_Z_E = constr_temp_LHS_Z_E[:-1]
        constr_Z_E = constr_temp_LHS_Z_E + "- Z_E_"+ str(t)+ "_" + str(j) + "= 0 \n"
        f.write("c"+str(constr_num)+":\t")
        constr_num += 1
        f.write(constr_Z_E)
       
###CC_N, G*_N, CC_E, G*_E
for j in range(int(len(J_list)/T)):
    for t in range(1, T+1):
        constr_temp_LHS_G_Star_N = ""
        constr_temp_LHS_G_Star_E = ""
        constr_temp_LHS_CC_N = ""
        constr_temp_LHS_CC_E = ""
        constr_temp_LHS_G_N = ""
        constr_temp_LHS_G_E = ""
        for k in range(T*j, T*(j+1)):
            constr_temp_LHS_G_Star_N += str(data[J_list[k]]["c"][0][str(t)][0]["1"][0]["N"][2]) + "pi_" + str(t) + "_" + str(k) + "_1_2 +" + str(data[J_list[k]]["c"][0][str(t)][0]["1"][0]["C, N"][5]) +"pi_" + str(t) + "_" + str(k) + "_4_5 +" 
            constr_temp_LHS_G_Star_E += str(data[J_list[k]]["c"][0][str(t)][0]["1"][0]["E"][2]) + "pi_" + str(t) + "_" + str(k) + "_2_2 +" + str(data[J_list[k]]["c"][0][str(t)][0]["1"][0]["C, E"][5]) +"pi_" + str(t) + "_" + str(k) + "_6_5 +"
            constr_temp_LHS_CC_N += str(data[J_list[k]]["c"][0][str(t)][0]["2"][0]["N"][1]) + "pi_" + str(t) + "_" + str(k) + "_1_1 +" + str(data[J_list[k]]["c"][0][str(t)][0]["2"][0]["C, N"][4]) +"pi_" + str(t) + "_" + str(k) + "_4_4 +" 
            constr_temp_LHS_CC_E += str(data[J_list[k]]["c"][0][str(t)][0]["2"][0]["E"][1]) + "pi_" + str(t) + "_" + str(k) + "_2_1 +" + str(data[J_list[k]]["c"][0][str(t)][0]["2"][0]["C, E"][4]) +"pi_" + str(t) + "_" + str(k) + "_6_4 +"
            constr_temp_LHS_G_N += str(data[J_list[k]]["c"][0][str(t)][0]["1"][0]["N"][1]) + "pi_" + str(t) + "_" + str(k) + "_1_1 +" + str(data[J_list[k]]["c"][0][str(t)][0]["1"][0]["G, N"][3]) +"pi_" + str(t) + "_" + str(k) + "_3_3 +"
            constr_temp_LHS_G_E += str(data[J_list[k]]["c"][0][str(t)][0]["1"][0]["E"][1]) + "pi_" + str(t) + "_" + str(k) + "_2_1 +" + str(data[J_list[k]]["c"][0][str(t)][0]["1"][0]["G, E"][3]) +"pi_" + str(t) + "_" + str(k) + "_5_3 +"               
        
        constr_temp_LHS_G_Star_N = constr_temp_LHS_G_Star_N[:-1]
        constr_temp_LHS_G_Star_E = constr_temp_LHS_G_Star_E[:-1]
        constr_temp_LHS_CC_N = constr_temp_LHS_CC_N[:-1]
        constr_temp_LHS_CC_E = constr_temp_LHS_CC_E[:-1]
        constr_temp_LHS_G_N = constr_temp_LHS_G_N[:-1]
        constr_temp_LHS_G_E = constr_temp_LHS_G_E[:-1]
        
        constr_G_Star_N = constr_temp_LHS_G_Star_N + "- G_Star_N_"+ str(t)+ "_" + str(j) + "= 0 \n"
        f.write("c"+str(constr_num)+":\t")
        constr_num += 1
        f.write(constr_G_Star_N)
        
        constr_G_Star_E = constr_temp_LHS_G_Star_E + "- G_Star_E_"+ str(t)+ "_" + str(j) + "= 0 \n"
        f.write("c"+str(constr_num)+":\t")
        constr_num += 1
        f.write(constr_G_Star_E)
        
        constr_CC_N = constr_temp_LHS_CC_N + "- CC_N_"+ str(t)+ "_" + str(j) + "= 0 \n"
        f.write("c"+str(constr_num)+":\t")
        constr_num += 1
        f.write(constr_CC_N)
        
        constr_CC_E = constr_temp_LHS_CC_E + "- CC_E_"+ str(t)+ "_" + str(j) + "= 0 \n"
        f.write("c"+str(constr_num)+":\t")
        constr_num += 1
        f.write(constr_CC_E)
        
        constr_G_N = constr_temp_LHS_G_N + "- G_N_"+ str(t)+ "_" + str(j) + "= 0 \n"
        f.write("c"+str(constr_num)+":\t")
        constr_num += 1
        f.write(constr_G_N)
        
        constr_G_E = constr_temp_LHS_G_E + "- G_E_"+ str(t)+ "_" + str(j) + "= 0 \n"
        f.write("c"+str(constr_num)+":\t")
        constr_num += 1
        f.write(constr_G_E)
 

f.write("Bounds \n")    

for t in range(1, T+2):
    for j in range(len(J_list)):
        for s in range(len(data[J_list[j]]['STATES'])):
            constr_temp = "sigma_" + str(t) + "_" + str(j) + "_" + str(s) + " >= 0\n"
            f.write(constr_temp) 

for t in range(1, T+1):
    for j in range(len(J_list)):
        for s in range(len(data[J_list[j]]['STATES'])):
            for a in range(len(data[J_list[j]]['ACTIONS'])): 
                constr_temp = "pi_" + str(t) + "_" + str(j) + "_" + str(s) + "_" + str(a) + ">= 0 \n"
                f.write(constr_temp) 
f.write("End") 
f.close()

pre, ext = os.path.splitext("opt.txt")
os.rename("opt.txt", pre + ".lp")