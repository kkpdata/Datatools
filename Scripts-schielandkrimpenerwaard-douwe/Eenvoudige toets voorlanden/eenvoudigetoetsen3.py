# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 14:41:31 2018

@author: yska
"""

import csv
import os
import tkinter.filedialog
import math
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

root = tkinter.Tk()
path = filedialog.askopenfilename(initialdir = os.getcwd(),title = "Selecteer bestand met karakteristieke punten",filetypes = (("CSV bestand","*.csv"),))
os.chdir(os.path.dirname(path))
path6 = filedialog.askopenfilename(initialdir = os.getcwd(),title = "Selecteer bestand met surfacelines",filetypes = (("CSV bestand","*.csv"),))

print(os.path.dirname(path))

newpath1 = os.path.dirname(path)+'/afbeeldingen_VLAF'
if not os.path.exists(newpath1):
    os.makedirs(newpath1)
path2 =  newpath1
newpath2 = os.path.dirname(path)+'/afbeeldingen_ZV'
if not os.path.exists(newpath2):
    os.makedirs(newpath2)
path3 =  newpath2

newpath3 = os.path.dirname(path)+'/CSVuitvoer'
if not os.path.exists(newpath3):
    os.makedirs(newpath3)
path4 =  newpath3
newpath4 = os.path.dirname(path)+'/profielen'
if not os.path.exists(newpath4):
    os.makedirs(newpath4)
path5 =  newpath4

root.destroy()

#maak leeg dataframe waar straks profielgegevens aan worden toegevoegd
dafra=pd.DataFrame([])


#lees sufacelines en maak losse csv's per profiel
cr2 = csv.reader(open(path6), delimiter=';')
firstline = True

for row in cr2:    
    if firstline:    #skip first line
        firstline = False
        continue
    profiel=row[0]
    d=row
    y=(np.array(d[1::3],dtype=float))
    x=(np.array(d[2::3],dtype=float))
    z=(np.array(d[3::3]))
    y=y-y[0]
    x=x-x[0]
    a=np.array(np.sqrt(x**2+y**2))

    df = pd.DataFrame({'x':x, 'y':y, 'z':z, 'a':a})
    df.columns=['a','x','y','z']
    
    df.to_csv(path5+"/"+profiel+'.csv',sep=';',header=True,index=False)

#open CSV bestand en lees waarden per rij uit
with open(path)as csvfile:
    cr = csv.DictReader(csvfile, delimiter=';')
    
    for row in cr:
        
        
        location =row['LOCATIONID']

        


        X_Mbu=float(row['X_Maaiveld buitenwaarts'])
        Y_Mbu=float(row['Y_Maaiveld buitenwaarts'])
        Z_Mbu=float(row['Z_Maaiveld buitenwaarts'])
        X_Tg=float(row['X_Teen geul'])
        Y_Tg=float(row['Y_Teen geul'])
        Z_Tg=float(row['Z_Teen geul'])
        X_Ig=float(row['X_Insteek geul'])
        Y_Ig=float(row['Y_Insteek geul'])
        Z_Ig=float(row['Z_Insteek geul'])
        X_Tdbu=float(row['X_Teen dijk buitenwaarts'])
        Y_Tdbu=float(row['Y_Teen dijk buitenwaarts'])
        Z_Tdbu=float(row['Z_Teen dijk buitenwaarts'])
        X_Kbub=float(row['X_Kruin buitenberm'])
        Y_Kbub=float(row['Y_Kruin buitenberm'])
        Z_Kbub=float(row['Z_Kruin buitenberm'])
        X_Ibub=float(row['X_Insteek buitenberm'])
        Y_Ibub=float(row['Y_Insteek buitenberm'])
        Z_Ibub=float(row['Z_Insteek buitenberm'])
        X_Kbu=float(row['X_Kruin buitentalud'])
        Y_Kbu=float(row['Y_Kruin buitentalud'])
        Z_Kbu=float(row['Z_Kruin buitentalud'])
        X_Kbi=float(row['X_Kruin binnentalud'])
        Y_Kbi=float(row['Y_Kruin binnentalud'])
        Z_Kbi=float(row['Z_Kruin binnentalud'])
        X_Ibib=float(row['X_Insteek binnenberm'])
        Y_Ibib=float(row['Y_Insteek binnenberm'])
        Z_Ibib=float(row['Z_Insteek binnenberm'])
        X_Kbib=float(row['X_Kruin binnenberm'])
        Y_Kbib=float(row['Y_Kruin binnenberm'])
        Z_Kbib=float(row['Z_Kruin binnenberm'])
        X_Tdbi=float(row['X_Teen dijk binnenwaarts'])
        Y_Tdbi=float(row['Y_Teen dijk binnenwaarts'])
        Z_Tdbi=float(row['Z_Teen dijk binnenwaarts'])
        X_Isd=float(row['X_Insteek sloot dijkzijde'])
        Y_Isd=float(row['Y_Insteek sloot dijkzijde'])
        Z_Isd=float(row['Z_Insteek sloot dijkzijde'])
        X_Bsd=float(row['X_Slootbodem dijkzijde'])
        Y_Bsd=float(row['Y_Slootbodem dijkzijde'])
        Z_Bsd=float(row['Z_Slootbodem dijkzijde'])
        X_Bsp=float(row['X_Slootbodem polderzijde'])
        Y_Bsp=float(row['Y_Slootbodem polderzijde'])
        Z_Bsp=float(row['Z_Slootbodem polderzijde'])
        X_Isp=float(row['X_Insteek sloot polderzijde'])
        Y_Isp=float(row['Y_Insteek sloot polderzijde'])
        Z_Isp=float(row['Z_Insteek sloot polderzijde'])
        X_Mbi=float(row['X_Maaiveld binnenwaarts'])
        Y_Mbi=float(row['Y_Maaiveld binnenwaarts'])
        Z_Mbi=float(row['Z_Maaiveld binnenwaarts'])


        #bereken de absolute afstand (van 3d naar 2d)
        #X en Y worden nX
        nX_Mbu=0
        
        if X_Tg !=-1:
            X_Tg=X_Tg-X_Mbu
            Y_Tg=Y_Tg-Y_Mbu
            nX_Tg=math.sqrt(X_Tg**2+Y_Tg**2)
        if X_Ig !=-1:
            X_Ig=X_Ig-X_Mbu
            Y_Ig=Y_Ig-Y_Mbu
            nX_Ig=math.sqrt(X_Ig**2+Y_Ig**2)
        X_Tdbu=X_Tdbu-X_Mbu
        Y_Tdbu=Y_Tdbu-Y_Mbu
        nX_Tdbu=math.sqrt(X_Tdbu**2+Y_Tdbu**2)
        if X_Kbub !=-1:
            X_Kbub=X_Kbub-X_Mbu
            Y_Kbub=Y_Kbub-Y_Mbu
            nX_Kbub=math.sqrt(X_Kbub**2+Y_Kbub**2)
        if X_Ibub !=-1:
            X_Ibub=X_Ibub-X_Mbu
            Y_Ibub=Y_Ibub-Y_Mbu
            nX_Ibub=math.sqrt(X_Ibub**2+Y_Ibub**2)
        X_Kbu=X_Kbu-X_Mbu
        Y_Kbu=Y_Kbu-Y_Mbu
        nX_Kbu=math.sqrt(X_Kbu**2+Y_Kbu**2)
        X_Kbi=X_Kbi-X_Mbu
        Y_Kbi=Y_Kbi-Y_Mbu
        nX_Kbi=math.sqrt(X_Kbi**2+Y_Kbi**2)
        if X_Kbib !=-1:
            X_Kbib=X_Kbib-X_Mbu
            Y_Kbib=Y_Kbib-Y_Mbu
            nX_Kbib=math.sqrt(X_Kbib**2+Y_Kbib**2)
        if X_Ibib !=-1:
            X_Ibib=X_Ibib-X_Mbu
            Y_Ibib=Y_Ibib-Y_Mbu
            nX_Ibib=math.sqrt(X_Ibib**2+Y_Ibib**2)
        X_Tdbi=X_Tdbi-X_Mbu
        Y_Tdbi=Y_Tdbi-Y_Mbu
        nX_Tdbi=math.sqrt(X_Tdbi**2+Y_Tdbi**2)
        if X_Isd != -1:
            X_Isd=X_Isd-X_Mbu
            Y_Isd=Y_Isd-Y_Mbu
            nX_Isd=math.sqrt(X_Isd**2+Y_Isd**2)
            X_Bsd=X_Bsd-X_Mbu
            Y_Bsd=Y_Bsd-Y_Mbu
            nX_Bsd=math.sqrt(X_Bsd**2+Y_Bsd**2)
            X_Bsp=X_Bsp-X_Mbu
            Y_Bsp=Y_Bsp-Y_Mbu
            nX_Bsp=math.sqrt(X_Bsp**2+Y_Bsp**2)
            X_Isp=X_Isp-X_Mbu
            Y_Isp=Y_Isp-Y_Mbu
            nX_Isp=math.sqrt(X_Isp**2+Y_Isp**2)
        X_Mbi=X_Mbi-X_Mbu
        Y_Mbi=Y_Mbi-Y_Mbu
        nX_Mbi=math.sqrt(X_Mbi**2+Y_Mbi**2)
        
        #maak afhankelijk van de aanwezige punten een dataframe per dwarsprofiel
        if X_Tg == -1:
            if X_Kbub ==-1:
                if X_Kbib ==-1:
                    if X_Isd == -1:
                        #1 geen geul, geen buitenberm, geen binnenberm, geen sloot
                        d = {'x': [nX_Mbu,nX_Tdbu,nX_Kbu,nX_Kbi,nX_Tdbi,nX_Mbi], 'z': [Z_Mbu,Z_Tdbu,Z_Kbu,Z_Kbi,Z_Tdbi,Z_Mbi],
                             'punt':['Maaiveld buitenwaards', 'teen dijk buiten', 'buitenkruin', 'binnenkruin', 
                            'teen dijk binnen','maaiveld binnen']}
                    else:                   #2 geen geul, geen buitenberm, geen binnenberm, wel sloot
                        d = {'x': [nX_Mbu,nX_Tdbu,nX_Kbu,nX_Kbi,nX_Tdbi,nX_Isd,nX_Bsd,nX_Bsp,nX_Isp,nX_Mbi], 
                             'z': [Z_Mbu,Z_Tdbu,Z_Kbu,Z_Kbi,Z_Tdbi,Z_Isd,Z_Bsd,Z_Bsp,Z_Isp,Z_Mbi],
                                'punt':['Maaiveld buitenwaards', 'teen dijk buiten', 'buitenkruin', 'binnenkruin',
                                'teen dijk binnen', 'insteek sloot dijkzijde', 'slootbodem dijkzijde', 'slootbodem polderzijde',
                                'insteek sloot dijkzijde','maaiveld binnen']}
                else:
                    if X_Isd == -1:
                        #1 geen geul, geen buitenberm, wel binnenberm, geen sloot
                        d = {'x': [nX_Mbu,nX_Tdbu,nX_Kbu,nX_Kbi,nX_Ibib, nX_Kbib, nX_Tdbi,nX_Mbi], 
                        'z': [Z_Mbu,Z_Tdbu,Z_Kbu,Z_Kbi,Z_Ibib, Z_Kbib,Z_Tdbi,Z_Mbi],
                        'punt':['Maaiveld buitenwaards', 'teen dijk buiten', 'buitenkruin', 'binnenkruin', 
                        'insteek binnenberm', 'kruin binnenberm','teen dijk binnen','maaiveld binnen']}
                    else:
                        #2 geen geul, geen buitenberm, wel binnenberm, wel sloot
                        d = {'x': [nX_Mbu,nX_Tdbu,nX_Kbu,nX_Kbi,nX_Tdbi,nX_Isd,nX_Bsd,nX_Bsp,nX_Isp,nX_Mbi], 
                        'z': [Z_Mbu,Z_Tdbu,Z_Kbu,Z_Kbi,Z_Tdbi,Z_Isd,Z_Bsd,Z_Bsp,Z_Isp,Z_Mbi],
                        'punt':['Maaiveld buitenwaards', 'teen dijk buiten', 'buitenkruin', 'binnenkruin', 'insteek binnenberm',
                        'kruin binnenberm','teen dijk binnen', 'insteek sloot dijkzijde', 'slootbodem dijkzijde', 'slootbodem polderzijde',
                        'insteek sloot dijkzijde','maaiveld binnen']}
            else:
                if X_Kbib ==-1:
                    if X_Isd == -1:
                        #3 geen geul,wel buitenberm, geen binnenberm, geen sloot
                        d = {'x': [nX_Mbu,nX_Tdbu,nX_Kbub,nX_Ibub, nX_Kbu,nX_Kbi,nX_Tdbi,nX_Mbi], 
                         'z': [Z_Mbu,Z_Tdbu,Z_Kbub,Z_Ibub,Z_Kbu,Z_Kbi,Z_Tdbi,Z_Mbi],
                                'punt':['Maaiveld buitenwaards', 'teen dijk buiten', 'kruin buitenberm', 
                                'insteek buitenberm', 'buitenkruin', 'binnenkruin', 'teen dijk binnen','maaiveld binnen']}
                    else:
                        #4 geen geul,wel buitenberm, geen binnenberm, wel sloot
                        d = {'x': [nX_Mbu,nX_Tdbu,nX_Kbub,nX_Ibub, nX_Kbu,nX_Kbi,nX_Tdbi,nX_Isd,nX_Bsd,nX_Bsp,nX_Isp,nX_Mbi], 
                        'z': [Z_Mbu,Z_Tdbu,Z_Kbub,Z_Ibub,Z_Kbu,Z_Kbi,Z_Tdbi,Z_Isd,Z_Bsd,Z_Bsp,Z_Isp,Z_Mbi],
                        'punt':['Maaiveld buitenwaards', 'teen dijk buiten', 'kruin buitenberm', 
                        'insteek buitenberm', 'buitenkruin', 'binnenkruin', 'teen dijk binnen', 'insteek sloot dijkzijde', 
                                'slootbodem dijkzijde', 'slootbodem polderzijde', 'insteek sloot dijkzijde','maaiveld binnen']}
                                        
    
                else:
                    if X_Isd == -1:
                        #5 geen geul,wel buitenberm, wel binnenberm, geen sloot
                        d = {'x': [nX_Mbu,nX_Tdbu,nX_Kbub,nX_Ibub,nX_Kbu,nX_Kbi,nX_Ibib, nX_Kbib,nX_Tdbi,nX_Mbi], 
                        'z': [Z_Mbu,Z_Tdbu,Z_Kbub,Z_Ibub,Z_Kbu,Z_Kbi,Z_Ibib, Z_Kbib,Z_Tdbi,Z_Mbi],
                        'punt':['Maaiveld buitenwaards', 'teen dijk buiten', 'kruin buitenberm', 
                        'insteek buitenberm', 'buitenkruin', 'binnenkruin', 'insteek binnenberm',
                        'kruin binnenberm', 'teen dijk binnen','maaiveld binnen']}
    
                    else:
                        #6 geen geul,wel buitenberm, wel binnenberm, wel sloot
                        d = {'x': [nX_Mbu,nX_Tdbu,nX_Kbub,nX_Ibub,nX_Kbu,nX_Kbi,nX_Ibib, nX_Kbib,nX_Tdbi,nX_Isd,nX_Bsd,
                        nX_Bsp,nX_Isp,nX_Mbi], 'z': [Z_Mbu,Z_Tdbu,Z_Kbub,Z_Ibub,Z_Kbu,Z_Kbi,Z_Ibib, Z_Kbib,
                        Z_Tdbi,Z_Isd,Z_Bsd,Z_Bsp,Z_Isp,Z_Mbi],
                        'punt':['Maaiveld buitenwaards', 'teen dijk buiten', 'kruin buitenberm', 
                        'insteek buitenberm', 'buitenkruin', 'binnenkruin', 'insteek binnenberm',
                        'kruin binnenberm', 'teen dijk binnen', 'insteek sloot dijkzijde', 
                        'slootbodem dijkzijde', 'slootbodem polderzijde', 'insteek sloot dijkzijde','maaiveld binnen']}
                                        
                            
        else:
            #geen buitenberm
            if X_Kbub ==-1:
                #geen binnenberm
                if X_Kbib ==-1:
                    #geen sloot
                    if X_Isd == -1:
                        #7 wel geul, geen buitenberm, geen binnenberm, geen sloot
                        d = {'x': [nX_Mbu,nX_Tg,nX_Ig,nX_Tdbu,nX_Kbu,nX_Kbi,nX_Tdbi,nX_Mbi], 
                        'z': [Z_Mbu,Z_Tg,Z_Ig,Z_Tdbu,Z_Kbu,Z_Kbi,Z_Tdbi,Z_Mbi], 
                        'punt':['Maaiveld buitenwaards', 'teen geul', 'insteek geul', 'teen dijk buiten', 
                        'buitenkruin', 'binnenkruin','teen dijk binnen', 'maaiveld binnen']}
                        #wel sloot
                    else:
                        #8 wel geul, geen buitenberm, geen binnenberm, wel sloot
                        d = {'x': [nX_Mbu,nX_Tg,nX_Ig,nX_Tdbu,nX_Kbu,nX_Kbi,nX_Tdbi,nX_Isd,nX_Bsd,nX_Bsp,nX_Isp,nX_Mbi], 
                        'z': [Z_Mbu,Z_Tg,Z_Ig,Z_Tdbu,Z_Kbu,Z_Kbi,Z_Tdbi,Z_Isd,Z_Bsd,Z_Bsp,Z_Isp,Z_Mbi], 
                        'punt':['Maaiveld buitenwaards', 'teen geul', 'insteek geul', 'teen dijk buiten', 
                        'buitenkruin', 'binnenkruin', 'teen dijk binnen','insteek sloot dijkzijde', 'slootbodem dijkzijde', 'slootbodem polderzijde', 
                        'insteek sloot dijkzijde', 'maaiveld binnen']}
                    #wel binnenberm
                else:
                    #geen sloot
                    if X_Isd == -1:
                        #9 wel geul, geen buitenberm, wel binnenberm, geen sloot
                        d = {'x': [nX_Mbu,nX_Tg,nX_Ig,nX_Tdbu,nX_Kbu,nX_Kbi,nX_Ibib,nX_Kbib,nX_Tdbi,nX_Mbi], 
                        'z': [Z_Mbu,Z_Tg,Z_Ig,Z_Tdbu,Z_Kbu,Z_Kbi,Z_Ibib, Z_Kbib,Z_Tdbi,Z_Mbi], 
                        'punt':['Maaiveld buitenwaards', 'teen geul', 'insteek geul', 'teen dijk buiten', 
                         'buitenkruin', 'binnenkruin','insteek binnenberm', 'kruin binnenberm', 'teen dijk binnen', 'maaiveld binnen']}
                    #wel sloot
                    else:
                        #10 wel geul, geen buitenberm, wel binnenberm, wel sloot
                        d = {'x': [nX_Mbu,nX_Tg,nX_Ig,nX_Tdbu,nX_Kbu,nX_Kbi,nX_Kbib,nX_Tdbi,nX_Tdbi,nX_Isd,nX_Bsd,nX_Bsp,nX_Isp,nX_Mbi], 
                        'z': [Z_Mbu,Z_Tg,Z_Ig,Z_Tdbu,Z_Kbu,Z_Kbi,Z_Tdbi,Z_Ibib, Z_Kbib,Z_Isd,Z_Bsd,Z_Bsp,Z_Isp,Z_Mbi], 
                        'punt':['Maaiveld buitenwaards', 'teen geul', 'insteek geul', 'teen dijk buiten', 
                         'buitenkruin', 'binnenkruin','insteek binnenberm', 'kruin binnenberm','teen dijk binnen',  'insteek sloot dijkzijde',
                        'slootbodem dijkzijde', 'slootbodem polderzijde', 'insteek sloot dijkzijde', 'maaiveld binnen']}                    
            #wel buitenberm
            else:
                #geen binnenberm
                if X_Kbib ==-1:
                    #geen sloot
                    if X_Isd == -1:
                        #11 wel geul,wel buitenberm, geen binnenberm, geen sloot
                        d = {'x': [nX_Mbu,nX_Tg,nX_Ig,nX_Tdbu,nX_Kbub,nX_Ibub, nX_Kbu,nX_Kbi,nX_Tdbi,nX_Mbi], 
                        'z': [Z_Mbu,Z_Tg,Z_Ig,Z_Tdbu,Z_Kbub,Z_Ibub,Z_Kbu,Z_Kbi,Z_Tdbi,Z_Mbi], 
                        'punt':['Maaiveld buitenwaards', 'teen geul', 'insteek geul', 'teen dijk buiten', 
                        'kruin buitenberm', 'insteek buitenberm', 'buitenkruin', 'binnenkruin', 'teen dijk binnen', 
                        'maaiveld binnen']}
                    #wel sloot
                    else:
                        #12 wel geul,wel buitenberm, geen binnenberm, wel sloot
                        d = {'x': [nX_Mbu,nX_Tg,nX_Ig,nX_Tdbu,nX_Kbub,nX_Ibub, nX_Kbu,nX_Kbi,nX_Tdbi,
                        nX_Isd,nX_Bsd,nX_Bsp,nX_Isp,nX_Mbi], 'z': [Z_Mbu,Z_Tg,Z_Ig,Z_Tdbu,Z_Kbub,
                        Z_Ibub,Z_Kbu,Z_Kbi,Z_Tdbi,Z_Isd,Z_Bsd,Z_Bsp,Z_Isp,Z_Mbi], 
                        'punt':['Maaiveld buitenwaards', 'teen geul', 'insteek geul', 'teen dijk buiten', 
                        'kruin buitenberm', 'insteek buitenberm', 'buitenkruin', 'binnenkruin',
                        'teen dijk binnen',  'insteek sloot dijkzijde', 'slootbodem dijkzijde',
                        'slootbodem polderzijde', 'insteek sloot dijkzijde', 'maaiveld binnen']}
                #wel binnenberm
                else:
                    #geen sloot
                    if X_Isd == -1:
                        #13 wel geul,wel buitenberm, wel binnenberm, geen sloot
                        d = {'x': [nX_Mbu,nX_Tg,nX_Ig,nX_Tdbu,nX_Kbub,nX_Ibub,nX_Kbu,nX_Kbi,nX_Ibib, 
                        nX_Kbib,nX_Tdbi,nX_Mbi], 'z': [Z_Mbu,Z_Tg,Z_Ig,Z_Tdbu,Z_Kbub,Z_Ibub, 
                        Z_Kbu,Z_Kbi,Z_Ibib, Z_Kbib,Z_Tdbi,Z_Mbi], 
                        'punt':['Maaiveld buitenwaards', 'teen geul', 'insteek geul', 'teen dijk buiten', 
                        'kruin buitenberm', 'insteek buitenberm', 'buitenkruin', 'binnenkruin',
                        'insteek binnenberm', 'kruin binnenberm', 'teen dijk binnen', 'maaiveld binnen']}
                    #wel sloot   
                    else:
                        #14 wel geul,wel buitenberm, wel binnenberm, wel sloot
                        d = {'x': [nX_Mbu,nX_Tg,nX_Ig,nX_Tdbu,nX_Kbub,nX_Ibub,nX_Kbu,nX_Kbi,nX_Ibib, 
                        nX_Kbib,nX_Tdbi,nX_Isd,nX_Bsd,nX_Bsp,nX_Isp,nX_Mbi], 
                        'z': [Z_Mbu,Z_Tg,Z_Ig,Z_Tdbu,Z_Kbub,Z_Ibub,Z_Kbu,Z_Kbi,Z_Ibib,
                        Z_Kbib,Z_Tdbi,Z_Isd,Z_Bsd,Z_Bsp,Z_Isp,Z_Mbi], 
                        'punt':['Maaiveld buitenwaards', 'teen geul', 'insteek geul', 'teen dijk buiten', 
                        'kruin buitenberm', 'insteek buitenberm', 'buitenkruin', 'binnenkruin',
                        'insteek binnenberm', 'kruin binnenberm', 'teen dijk binnen', 'insteek sloot dijkzijde', 
                        'slootbodem dijkzijde', 'slootbodem polderzijde', 'insteek sloot dijkzijde', 
                        'maaiveld binnen']}
        
                        
                        
            
        df_dijk=pd.DataFrame(data=d)
        #bereken het talud (met twee tussenstappen)
        df_dijk["dx"] = -1*df_dijk["x"].diff(-1)
        df_dijk["dz"] = -1*df_dijk["z"].diff(-1)
        df_dijk['helling']=abs(df_dijk['dx']/df_dijk['dz'])
        df_dijk.set_index('punt', inplace=True)
        
        df_dijk.to_csv(path4+'\\'+location+'.csv',sep=';')
        
        #laat geometrien uit map
        #indien je deze bestanden niet hebt comment deze code 
        file2=path5+"/"+location+'.csv'
        #print(file2)
        with open(file2) as csvfile:
            cr = csv.DictReader(csvfile, delimiter=';')
      
            x=[]
            y=[]
            z=[]
            a=[]
            for row in cr:
                
                xen=float(row['x'])
                x.append(xen)
                yen=float(row['y'])
                y.append(yen)
                zen=float(row['z'])
                z.append(zen)
                aen=float(row['a'])
                a.append(aen)
    
            
            #print (a[0])
            a=np.array(a)
            
            a=a-a[0]
            #print (a)
    
            profieltot=pd.DataFrame({ "x":x,"y":y, "z":z, "a":a}) 
            
       # print(profieltot)    
                    

        
        
        #zonder geul geen voorlandbeoordeling
        if X_Tg !=-1:
            #hoogte geul
            dz_geul = Z_Tdbu -Z_Tg
            #VLAF
            #invloedzone
            ivz =15
            #helling signaleringsprofiel
            helsp=6
            #marge signaleringsprofiel
            msp=1.5
            
            
            #signaleringsprofiel
            #knik signaleringsprofiel
            x_ksp=nX_Tdbu-ivz-(dz_geul*msp)
            z_ksp=Z_Tdbu
            #onderkant signaleringsprofiel
            x_osp=nX_Tdbu-ivz-(dz_geul*(helsp+msp))
            z_osp=Z_Tg
            s={'x':[x_osp,x_ksp,nX_Tdbu-ivz],'z':[z_osp,z_ksp,Z_Tdbu]}
            df_sig=pd.DataFrame(data=s)
                
            #rekenprofiel
            #knik rekenprofiel
            #helling geul
            helg=df_dijk.iloc[1,4]
            #hoogte geul
            hg=df_dijk.iloc[1,3]+df_dijk.iloc[2,3]
        
            x_krp=nX_Tg+helg*hg
            z_krp=Z_Tdbu
            df_rek={'x':[nX_Tg,x_krp],'z':[Z_Tg,z_krp]}
    
            #bepaling Saf
            x_saf=nX_Tg+helg*hg*0.5
            z_saf=Z_Tg+0.5*hg
            
            #bepaling Ssign
            x_ssign=x_osp+hg*(helsp/2)
            z_ssign=z_saf
            
            #bepaling oordeel
            if x_saf<x_ssign:
                oordeel='voldoet'
                plt.text(10, 5, oordeel,bbox={'facecolor':'green', 'alpha':10, 'pad':10})
            else:
                oordeel='verder beoordelen'
                plt.text(x_osp, 5, oordeel,bbox={'facecolor':'red', 'alpha':10, 'pad':10})
            
                
            
            #print(df_dijk)
            plt.ylim(-10,8)
            plt.xlabel("Afstand [m]")
            plt.title('Eenvoudige toets VLAF '+location)
            plt.ylabel("Hoogte [m t.o.v. NAP]")
            Profiel_dijk,=plt.plot(profieltot['a'], profieltot['z'],color='grey',linewidth=1.0,label='Profiel')
            plt.plot([x_saf], [z_saf],'ro',color='yellow',)
            plt.plot([x_ssign], [z_ssign],'ro',color='orange',)
            Schematisatie,=plt.plot(df_dijk['x'], df_dijk['z'],color='green',linewidth=2.0,label='Schematisatie')
            Signaleringsprofiel,=plt.plot(df_sig['x'], df_sig['z'],color='red',linewidth=2.0,label='Signaleringsprofiel')
            Rekenprofiel,=plt.plot(df_rek['x'], df_rek['z'],color='blue',linewidth=2.0,label='Rekenprofiel')
            plt.legend(loc='lower right', handles=[Profiel_dijk,Schematisatie,Signaleringsprofiel,Rekenprofiel ])
        
            
            plt.savefig(path2+"\\"+"VLAF_"+location+'.png')
            plt.show()
            
            
           
            #Zettingsvloeiing
            #invloedzone
            ivz =15
            #helling signaleringsprofiel
            if dz_geul<40:
                helsp=15
            else:
                helsp=20
            #marge signaleringsprofiel
            msp=2
            
            
            #signaleringsprofiel
            #knik signaleringsprofiel
            x_ksp=nX_Tdbu-ivz-(dz_geul*msp)
            z_ksp=Z_Tdbu
            #onderkant signaleringsprofiel
            x_osp=nX_Tdbu-ivz-(dz_geul*(helsp+msp))
            z_osp=Z_Tg
            s={'x':[x_osp,x_ksp,nX_Tdbu-ivz],'z':[z_osp,z_ksp,Z_Tdbu]}
            df_sig=pd.DataFrame(data=s)
            
            #rekenprofiel
            #knik rekenprofiel
            #helling geul
            helg=df_dijk.iloc[1,4]
            #hoogte geul
            hg=df_dijk.iloc[1,3]+df_dijk.iloc[2,3]
               
            x_krp=nX_Tg+helg*hg
            z_krp=Z_Tdbu
            df_rek={'x':[nX_Tg,x_krp],'z':[Z_Tg,z_krp]}
        
            #bepaling Saf
            x_saf=nX_Tg+helg*hg*(1/3)
            z_saf=Z_Tg+(1/3)*hg
    
            #bepaling Ssign
            x_ssign=x_osp+hg*(helsp/3)
            z_ssign=z_saf
                
            #bepaling oordeel
            if x_saf<x_ssign:
                oordeel='voldoet'
                plt.text(10, 5, oordeel,bbox={'facecolor':'green', 'alpha':10, 'pad':10})
            else:
                oordeel='verder beoordelen'
                plt.text(x_osp, 5, oordeel,bbox={'facecolor':'red', 'alpha':10, 'pad':10})
                    
            plt.ylim(-10,8)
            plt.xlabel("Afstand [m]")
            plt.title('Eenvoudige toets Zettingsvloeiing '+location)
            plt.ylabel("Hoogte [m t.o.v. NAP]")
            Profiel_dijk,=plt.plot(profieltot['a'], profieltot['z'],color='grey',linewidth=1.0,label='Profiel')
            plt.plot([x_saf], [z_saf],'ro',color='yellow',)
            plt.plot([x_ssign], [z_ssign],'ro',color='orange',)
            Schematisatie,=plt.plot(df_dijk['x'], df_dijk['z'],color='green',linewidth=2.0,label='Schematisatie')
            Signaleringsprofiel,=plt.plot(df_sig['x'], df_sig['z'],color='red',linewidth=2.0,label='Signaleringsprofiel')
            Rekenprofiel,=plt.plot(df_rek['x'], df_rek['z'],color='blue',linewidth=2.0,label='Rekenprofiel')
            plt.legend(loc='lower right', handles=[Profiel_dijk,Schematisatie,Signaleringsprofiel,Rekenprofiel ])
            plt.savefig(path3+"\\"+"ZV_"+location+'.png')
            plt.show()
                
         
            
            #breedte en hoogte voorland
            bv=nX_Tdbu-nX_Ig
            hv = (Z_Ig+Z_Tdbu)/2
    
            
                
            #maak dataframe met eigenschappen
            df = pd.DataFrame({'locatie':location, 'breedte voorland':bv, 'hoogte voorland':hv}, index=[0])
            #voeg dataframe toe aan de dataframe waar alle profielen in komen
            dafra=dafra.append(df)
            #leeg oorspronkelijke dataframe
            df=pd.DataFrame([])
            
        else:
            print(location+'heeft geen geul')

#exporteer dataframe naar csv bestand
dafra.to_csv(os.path.dirname(path)+'\\'+'hoogte_breedte.csv',sep=';',header=False,index=False)