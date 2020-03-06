#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf 
from scipy import stats
import statsmodels.api as sm

rf_df = pd.read_csv("./rf.csv")
rm_df = pd.read_csv("./rm.csv")

### Rf
rf = rf_df["rf"].values[:-1]
rf = [float(e) for e in list(rf)]

### Rm
rm_adj_close = rm_df['Adj_Close'].values
rm = []
for i in range(len(rm_adj_close)):
    if (i != 0):
        rm.append(round(float((rm_adj_close[i] - rm_adj_close[i - 1])/rm_adj_close[i - 1] * 100), 2))

### slice ri 
ri_df = pd.read_csv("./_historial_price_Bid-Ask full data_new.csv")

def sp0(string):
    return int(string.split("/")[0])

def sp1(string):
    return int(string.split("/")[1])

def sp2(string):
    return int(string.split("/")[2])

ri_dict = {}
for name,group in ri_df.groupby(['Company']):
    date_close_table = group[::-1][["Date","Adj Close"]]
    date_close_table["Month"] = date_close_table["Date"].apply(sp0)
    date_close_table["Day"] = date_close_table["Date"].apply(sp1)
    date_close_table["Year"] = date_close_table["Date"].apply(sp2)
    if name not in ['Canopy Growth Corporation', 'Hydro One Limited', 'Kinaxis', 'Zymeworks']:
        ri_adj = []
        for n, g in date_close_table.groupby(["Year", "Month"]):
            adj_close_arr = g["Adj Close"].values
            ri_adj.append(adj_close_arr[0])
        ri = []
        for i in range(len(ri_adj)):
            if (i != 0):
                ri.append(round(float((ri_adj[i] - ri_adj[i - 1])/ri_adj[i - 1] * 100), 2))
        ri_dict[name] = ri

### slice mom
mom_dict = {}
mom_df = pd.read_csv("./_historial_price_Bid-Ask full data_new.csv")
for name, group in mom_df.groupby(["Company"]):
    date_close_table = group[["Company","Date","Adj Close"]]
    date_close_table["Month"] = date_close_table["Date"].apply(sp0)
    date_close_table["Day"] = date_close_table["Date"].apply(sp1)
    date_close_table["Year"] = date_close_table["Date"].apply(sp2)
    mom_monthly = []
    if name not in ['Canopy Growth Corporation', 'Hydro One Limited', 'Kinaxis', 'Zymeworks']:
        for n,g in date_close_table.groupby(["Year", "Month"]):
            mom_monthly.append(g[::-1]["Adj Close"].values[0])
        mom_month = []
        for i in range(len(mom_monthly)):
            if (i != 0):
                mom_month.append(round(float(mom_monthly[i] - mom_monthly[i-1]), 2))
        mom_dict[name] = mom_month

### SMB 
PFC = ri_dict["Parkland Fuel Corporation"] # small
RBC = ri_dict["Royal Bank of Canada"] # big
SMB = np.array(PFC) - np.array(RBC)

### OLS
result_list = {}
for key in ri_dict.keys():
    print "\n\n\n[=========================" + str(key) + "===========================]"
    ri_rf = np.array(ri_dict[key]) - np.array(rf)
    rm_rf = np.array(rm) - np.array(rf)
    smb = SMB
    mom = np.array(mom_dict[key])
    #######################################
    y = ri_rf
    X = np.array([rm_rf, smb, mom]).T
    result = sm.OLS(y, X).fit()
    print result.summary()
    result_list[key] = result

