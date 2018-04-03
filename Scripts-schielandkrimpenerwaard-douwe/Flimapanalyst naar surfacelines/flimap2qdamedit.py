
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  31 10:49:37 2018

@author: yska
"""
#importeer libraries
import matplotlib.pyplot as plt
import glob
import numpy as np
import pandas as pd
import os
import tkinter.filedialog
from tkinter import filedialog

#bepaal invoer en uitvoermap
root = tkinter.Tk()
path = tkinter.filedialog.askdirectory(parent=root,initialdir="/",title='Selecteer map met flimapprofielen')
path2 = root.filename =  filedialog.asksaveasfilename(initialdir = "/",title = "Select file",filetypes = (("CSV bestand","*.csv"),))
allFiles1 = glob.glob(path + "/*.txt")

#verander txt ebstanden in csv bestanden
for file_ in allFiles1:
    thisFile = file_
    base = os.path.splitext(thisFile)[0]
    os.rename(thisFile, base + ".csv")

#gebruik alle csv bestanden in een map
allFiles = glob.glob(path + "/*.csv")

#creeer lege araays voor de waarden x,y en z
x=[]
y=[]
z=[]

#maak leeg dataframe waar straks profielgegevens aan worden toegevoegd
dafra=pd.DataFrame([])

#verander kommas in punten
def conv(x):
    return x.replace(',', '.').encode()

#voor alle csv bestanden in opgegeven map
for file_ in allFiles:
    #bepaal titel op basis van naam csv bestand
    titel=file_[len(path)+1:-4]
    #open het bestand
    with open(file_, 'r') as csvfile:
        #maak dataframe van csv bestand
        plots= np.genfromtxt((conv(x) for x in open(file_)), delimiter=';',skip_header=10,names=['volgorde','x','y','Afstand', 'Z'])
    #voeg voor elke rij de x waarde toe aan de x array enz.
    for row in plots:
        x.append((row[1]))
        y.append((row[2]))
        z.append((row[3]))
    #maak een dataframe met x,y en z als kolommen
    df = pd.DataFrame({'x':x, 'y':y, 'z':z})
    #transponeer dataframe zodat alle rijen achter elkaar komen te staan
    df = pd.DataFrame(df.stack().to_frame().values).T
    #voeg de naam van het profiel toe op basis van de titel van het bestand
    df.insert(loc=0, column='naam', value=[titel])
    #voeg dataframe toe aan de dataframe waar alle profielen in komen
    dafra=dafra.append(df)
    #leeg oorspronkelijke dataframe
    df=pd.DataFrame([])
    #leeg de arrays voor volgende grafiek
    x=[]
    y=[]
    z=[]

#maak een dataframe met de titels
df2 = pd.DataFrame([['LOCATIONID','X1','Y1','Z1','.....','Xn','Yn','Zn',"(Profiel)"]],columns=['naam',0,1,2,3,4,5,6,7])
#voeg de titels toe aan einddataframe
dafra=pd.concat([df2,dafra])
#exporteer dataframe naar csv bestand
dafra.to_csv(path2+'.csv',sep=';',header=False,index=False)
