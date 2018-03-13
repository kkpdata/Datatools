# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 09:13:25 2017

@author: Thijs IJPelaar

Dit script maakt BM-grasbestanden op basis van een templatebestand (templace.grsx) en
een Exceldocument met de input

"""

import xml.etree.cElementTree as ET
import pandas as pd
import os

#Aan te passen variabele:
file = 'input_ps_1-30dsn.xlsx'

#Inladen inputgegevens
xl = pd.ExcelFile(os.path.join(file))
df = xl.parse('Blad1')

# Open het templatebestand
tree = ET.ElementTree(file='template.grsx')

#Ga alle rijen van het Exceldocument af 
for i in range(0,df.shape[0]):
    
    #Ga naar golfklap
    for ip in tree.iter(tag='Input'):
        
        #Als het gaat om de input van golfklap
        if ip.attrib['Key'] == '8':
    
            #Ga alle keys in input af en vul ze aan        
            keys = ['Fsand','ConstantA','ConstantB','ConstantC','ZswlMax','ZswlMin','Hm0Max','Hm0Min','DeltaZ','ZGrassMax','ZGrassMin','Dcombined']
            for key in keys:
                ip.attrib[key] = str(df[key][i])
      
    #Pas de waterstanden aan
    for wl in tree.iter(tag='WaterLevel'):
        if 'Key' in wl.attrib.keys():        
            wl.attrib['Zswl'] = str(df['Zswl1'][i])
        
    #Pas de Qvariant aan
    for qv in tree.iter(tag='QVarian'):
        
        if qv.attrib['Key'] == '12':
            qv.attrib['Zswl'] = str(df['Qws1'][i])
            qv.attrib['Hm0'] = str(df['QHm0'][i])
            
        if qv.attrib['Key'] == '13':
            qv.attrib['Zswl'] = str(df['Qws2'][i])
            qv.attrib['Hm0'] = str(df['QHm0'][i])

    #Schrijf nu het bestand uit
    if not os.path.exists('Output/'):
        os.makedirs('Output/')
    tree.write('Output/'+df['Name'][i]+".grsx")







