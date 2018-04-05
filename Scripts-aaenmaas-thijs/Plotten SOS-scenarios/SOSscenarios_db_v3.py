# -*- coding: utf-8 -*-
# Mirjam Flierman, 2018

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sqlite3
import pandas as pd

# Aanpassen directory
directory       = r'C:\\pad\naar\Input'
soilbestandnaam = 'voorbeeld.soil'
lengtesementnaam= 15 #Aantal tekens dat wordt meegenomen in de segmentnaamgeving (zie regel 68)

# kleurcodes aanpassen
def getRGBfromI(RGBint):
    blue =  RGBint & 255
    green = (RGBint >> 8) & 255
    red =   (RGBint >> 16) & 255
    return (red, green, blue)

#Maak een connectie met de database en extraheer alle relevante data
os.chdir(directory)
con = sqlite3.connect(soilbestandnaam)
cur = con.cursor()

#Pak nu de benodigde data uit de database
soillayer1d     = pd.read_sql_query("select * from SoilLayer1D;", con)
materials       = pd.read_sql_query("select * from Materials;", con)
soilprofile1d   = pd.read_sql_query("select * from SoilProfile1D;", con)
stochastics     = pd.read_sql_query("select * from StochasticSoilProfile;", con)
colors          = pd.read_sql_query("select * from ParameterValues where PN_ID == 1;", con)

#Maak een samenvatting van de belangrijke data, dit is een overzicht van álle lagen
summary             = pd.DataFrame(columns=['SP1D_ID','SP1D_Name','MA_ID','MA_Name','TopLevel','BottomLevel','colortext','kans','segment','materiaal'])
summary['SP1D_ID']  = soillayer1d['SP1D_ID'].copy()
summary['MA_ID']    = soillayer1d['MA_ID']
summary['TopLevel'] = soillayer1d['TopLevel']

for index, row in summary.iterrows():
    try:
        #Zoek de 1D profielnamen per laag en de kans per laag
        summary.set_value(index,'SP1D_Name',    soilprofile1d['SP1D_Name'][soilprofile1d['SP1D_ID'] == row['SP1D_ID']].tolist()[0])
        summary.set_value(index,'kans',         stochastics['Probability'][stochastics['SP1D_ID'] == row['SP1D_ID']].tolist()[0])
        #Zoek de materiaalnamen en kleuren
        summary.set_value(index,'MA_Name',      materials['MA_Name'][materials['MA_ID'] == row['MA_ID']].tolist()[0])
        summary.set_value(index,'colortext',    getRGBfromI(int(colors['PV_Value'][colors['MA_ID'] == row['MA_ID']].tolist()[0])))
    except:
        print("Eroroooor")
    
    #Zoek de bottomlevel
    
    if index < summary.shape[0]-1: #Als niet de laatste
        nextLevel = summary.TopLevel[index+1]
        if nextLevel < row.TopLevel: #Als de volgende laag nog steeds bij dit profiel hoort
            summary.set_value(index,'BottomLevel', summary.TopLevel[index+1])
        else: #Als een nieuw profiel begonnen wordt 
            summary.set_value(index,'BottomLevel', -40)
    else: #De allerlaatste waarde
        summary.set_value(index,'BottomLevel', -40)

con.close()

SP1D_Name   = summary.SP1D_Name.values

# segment namen
summary = summary.dropna(subset=['MA_Name'])
summary['segment']  = [seg[:lengtesementnaam] for seg in summary.SP1D_Name]
summary['materiaal']= [seg.split('_',maxsplit=2)[2] for seg in summary.MA_Name]
segment_names       = list(set(summary.segment))
    
""" plot"""
for s in segment_names:

    fig1 = plt.figure(figsize=(10, 4), facecolor='w', edgecolor='k')
    ax1 = fig1.add_subplot(111)
    
    # scenarios horende bij het segment
    summary_per_segment = summary.loc[summary['segment'] == s]
    summary_per_segment.sort_values(by=['SP1D_ID'])
    unique_scenario = list(set(summary_per_segment.SP1D_ID))
    unique_scenario.sort()
    
    x,scenarios =[],[]
    
    j=0

    for i in unique_scenario:
        
        j=j+1
    
        temp = summary_per_segment.loc[summary['SP1D_ID'] == i]
                
        for index,row in temp.iterrows():
            db  = row.BottomLevel
            dt  = row.TopLevel
            col = tuple([x/255 for x in row.colortext])
            ax1.add_patch(patches.Rectangle((j*2+1, db), 1, dt-db,linewidth=0,facecolor=col))
                
            plt.text(j*2+1.5, -35, (str(int(row.kans*100)) + '%'),horizontalalignment='center', fontsize=8)
                
        x.append(j*2+1.5)
        scenarios.append(row.SP1D_Name[15:len(row.SP1D_Name)])
    
    plt.xlabel('scenario [-]')
    plt.ylabel('diepte [m+NAP]')
    plt.title(s)
    axes = plt.gca()
    axes.set_xlim([2.5,j*2+2.5])
    plt.xticks(x,scenarios)
    axes.set_ylim([-40,20])
    
    # legenda toevoegen        
    patchs = []
    
    # materialen die voorkomen in dit segment
    unique_material = list(set(summary_per_segment.MA_ID))
    
    for k in unique_material:
        materiaalnaam   = summary_per_segment.loc[summary['MA_ID'] == k].materiaal.get_values()[0]
        kleur           = summary_per_segment.loc[summary['MA_ID'] == k].colortext.get_values()[0]
        kleur           = tuple([x/255 for x in kleur])
        red_patch = patches.Patch(facecolor=kleur, label=materiaalnaam)
        patchs.append(red_patch)
            
    lgd = plt.legend(handles=patchs,bbox_to_anchor=(1.17,0.1),loc=4)

    plt.grid(which='major', axis='y')
    
    figname = (s+'.png')
    fig1.savefig(figname, dpi=500, bbox_extra_artists=(lgd,), bbox_inches='tight')
    
    plt.close(fig1)

plt.close("all")
