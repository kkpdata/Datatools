# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 14:24:02 2018

@author: yska
"""

import xml.etree.ElementTree as ET
import pandas as pd
import csv
import tkinter.filedialog
from tkinter import filedialog


root = tkinter.Tk()
path = filedialog.askopenfilename(initialdir = "/",title = "Selecteer kunstwerkeninvoerbestand",filetypes = (("Excel bestand","*.xlsx"),))
path2 = root.filename =  filedialog.asksaveasfilename(initialdir = "/",title = "Opslaan als... ",filetypes = (("XML bestand","*.xml"),))
root.destroy()





file_name =  path
sheet =  1


data2 = ET.Element('configuratie')


df = pd.read_excel(io=file_name, sheet_name=sheet)
#print(df.head(5))  # print first 5 rows of the dataframe
df = df.T
header = df.iloc[0]
df = df[1:]
df = df.rename( columns = header)
df.to_csv('hallo.csv', sep=";")
#print(df)  

data = ET.Element('configuratie')
with open("hallo.csv", 'rU')as csvfile:
    cr = csv.DictReader(csvfile, delimiter=';')
    
    for row in cr:
        vld= row['voorlandprofiel']
        
        # create the file structure

        berekening = ET.SubElement(data, 'berekening')
        berekening.set('naam',row['kunstwerk'])
        item1 = ET.SubElement(berekening, 'hrlocatie')
        item2 = ET.SubElement(berekening, 'kunstwerk')
        item3 = ET.SubElement(berekening, 'orientatie')
        item4 = ET.SubElement(berekening, 'faalkansgegevenerosiebodem')
        if vld:
            print (vld)
            item44 = ET.SubElement(berekening, 'voorlandprofiel')
            golfreductie = ET.SubElement(berekening, 'golfreductie')
            item45 = ET.SubElement(golfreductie, 'damgebruiken')
            item46 = ET.SubElement(golfreductie, 'damtype')
            item47 = ET.SubElement(golfreductie, 'damhoogte')
            item48 = ET.SubElement(golfreductie, 'voorlandgebruiken')
            item44.text = row['voorlandprofiel']
            item45.text = row['damgebruiken']
            item46.text = row['damtype']
            item47.text = row['damhoogte']
            item48.text = row['voorlandgebruiken']
        stochasten = ET.SubElement(berekening, 'stochasten')
        breedtebodembescherming= ET.SubElement(stochasten,'stochast')
        breedtebodembescherming.set('naam','breedtebodembescherming')
        item13=ET.SubElement(breedtebodembescherming,'verwachtingswaarde')
        item14=ET.SubElement(breedtebodembescherming, 'standaardafwijking')
        breedtedoorstroomopening= ET.SubElement(stochasten,'stochast')
        breedtedoorstroomopening.set('naam','breedtedoorstroomopening')
        item15=ET.SubElement(breedtedoorstroomopening,'verwachtingswaarde')
        item16=ET.SubElement(breedtedoorstroomopening, 'standaardafwijking')
        kombergendoppervlak= ET.SubElement(stochasten,'stochast')
        kombergendoppervlak.set('naam','kombergendoppervlak')
        item17=ET.SubElement(kombergendoppervlak,'verwachtingswaarde')
        item18=ET.SubElement(kombergendoppervlak, 'variatiecoefficient')
        kritiekinstromenddebiet= ET.SubElement(stochasten,'stochast')
        kritiekinstromenddebiet.set('naam','kritiekinstromenddebiet')
        item19=ET.SubElement(kritiekinstromenddebiet,'verwachtingswaarde')
        item20=ET.SubElement(kritiekinstromenddebiet, 'variatiecoefficient')
        modelfactoroverloopdebiet = ET.SubElement(stochasten,'stochast')
        modelfactoroverloopdebiet.set('naam','modelfactoroverloopdebiet')
        item21=ET.SubElement(modelfactoroverloopdebiet,'verwachtingswaarde')
        peilverhogingkomberging= ET.SubElement(stochasten,'stochast')
        peilverhogingkomberging.set('naam','peilverhogingkomberging')
        item22=ET.SubElement(peilverhogingkomberging,'verwachtingswaarde')
        item23=ET.SubElement(peilverhogingkomberging, 'standaardafwijking')
        stormduur = ET.SubElement(stochasten,'stochast')
        stormduur.set('naam','stormduur')
        item24=ET.SubElement(stormduur,'verwachtingswaarde')
        kerendehoogte= ET.SubElement(stochasten,'stochast')
        kerendehoogte.set('naam','kerendehoogte')
        item41=ET.SubElement(kerendehoogte,'verwachtingswaarde')
        item42=ET.SubElement(kerendehoogte, 'standaardafwijking')
        item43 = ET.SubElement(berekening, 'illustratiepunteninlezen')

        item1.text = row['hrlocatie']
        item2.text = row['kunstwerk']
        item3.text = row['orientatie']
        item4.text = row['faalkansgegevenerosiebodem']
        item13.text = row['breedtebodembescherming']
        item14.text = row['sabreedtebodembescherming']
        item15.text = row['breedtedoorstroomopening']
        item16.text = row['sabreedtedoorstroomopening']
        item17.text = row['kombergendoppervlak']
        item18.text = row['vckombergendoppervlak']
        item19.text = row['kritiekinstromenddebiet']
        item20.text = row['vckritiekinstromenddebiet']
        item21.text = row['modelfactoroverloopdebiet']
        item22.text = row['peilverhogingkomberging']
        item23.text = row['sapeilverhogingkomberging']
        item24.text = row['stormduur']
        item41.text = row['kerendehoogte']
        item42.text = row['sakerendehoogte']
        item43.text = row['illustratiepunteninlezen']




# create a new XML file with the results
mydata = ET.tostring(data)
myfile = open(path2+".xml", "wb")
myfile.write(mydata)
myfile.close()













#
#
#
#
#
#
#for index, row in df.iterrows():
#    print (df.loc[[row],['hrlocatie']])
#    
#    # create the file structure
#    berekening = ET.SubElement(data2, 'berekening')
#
#  
#    item1 = ET.SubElement(berekening, 'hrlocatie')
#    item2 = ET.SubElement(berekening, 'kunstwerk')
#    item3 = ET.SubElement(berekening, 'orientatie')
#    item4 = ET.SubElement(berekening, 'faalkansgegevenerosiebodem')
#    stochasten = ET.SubElement(berekening, 'stochasten')
#    breedtebodembescherming= ET.SubElement(stochasten,'stochast')
#    breedtebodembescherming.set('naam','breedtebodembescherming')
#    item13=ET.SubElement(breedtebodembescherming,'verwachtingswaarde')
#    item14=ET.SubElement(breedtebodembescherming, 'standaardafwijking')
#    breedtedoorstroomopening= ET.SubElement(stochasten,'stochast')
#    breedtedoorstroomopening.set('naam','breedtedoorstroomopening')
#    item15=ET.SubElement(breedtedoorstroomopening,'verwachtingswaarde')
#    item16=ET.SubElement(breedtedoorstroomopening, 'standaardafwijking')
#    kombergendoppervlak= ET.SubElement(stochasten,'stochast')
#    kombergendoppervlak.set('naam','kombergendoppervlak')
#    item17=ET.SubElement(kombergendoppervlak,'verwachtingswaarde')
#    item18=ET.SubElement(kombergendoppervlak, 'variatiecoefficient')
#    kritiekinstromenddebiet= ET.SubElement(stochasten,'stochast')
#    kritiekinstromenddebiet.set('naam','kritiekinstromenddebiet')
#    item19=ET.SubElement(kritiekinstromenddebiet,'verwachtingswaarde')
#    item20=ET.SubElement(kritiekinstromenddebiet, 'variatiecoefficient')
#    modelfactoroverloopdebiet = ET.SubElement(stochasten,'stochast')
#    modelfactoroverloopdebiet.set('naam','modelfactoroverloopdebiet')
#    item21=ET.SubElement(modelfactoroverloopdebiet,'verwachtingswaarde')
#    peilverhogingkomberging= ET.SubElement(stochasten,'stochast')
#    peilverhogingkomberging.set('naam','peilverhogingkomberging')
#    item22=ET.SubElement(peilverhogingkomberging,'verwachtingswaarde')
#    item23=ET.SubElement(peilverhogingkomberging, 'standaardafwijking')
#    stormduur = ET.SubElement(stochasten,'stochast')
#    stormduur.set('naam','stormduur')
#    item24=ET.SubElement(stormduur,'verwachtingswaarde')
#    kerendehoogte= ET.SubElement(stochasten,'stochast')
#    kerendehoogte.set('naam','kerendehoogte')
#    item41=ET.SubElement(kerendehoogte,'verwachtingswaarde')
#    item42=ET.SubElement(kerendehoogte, 'standaardafwijking')
#    
#    berekening.set('naam',(df.loc[row],['berekeningnaam']) ) 
#    item1.text = df.loc[row],['hrlocatie']
#    item2.text = (df.loc[row],['kunstwerk'])
#    item3.text = (df.loc[row],['orientatie'])
#    item4.text = (df.loc[row],['faalkansgegevenerosiebodem'])
#    item13.text = (df.loc[row],['breedtebodembescherming'])
#    item14.text = (df.loc[row],['sabreedtebodembescherming'])
#    item15.text = (df.loc[row],['breedtedoorstroomopening'])
#    item16.text = (df.loc[row],['sabreedtedoorstroomopening'])
#    item17.text = (df.loc[row],['kombergendoppervlak'])
#    item18.text = (df.loc[row],['vckombergendoppervlak'])
#    item19.text = (df.loc[row],['kritiekinstromenddebiet'])
#    item20.text = (df.loc[row],['vckritiekinstromenddebiet'])
#    item21.text = (df.loc[row],['modelfactoroverloopdebiet'])
#    item22.text = (df.loc[row],['peilverhogingkomberging'])
#    item23.text = (df.loc[row],['sapeilverhogingkomberging'])
#    item24.text = (df.loc[row],['stormduur'])
#    item41.text = (df.loc[row],['kerendehoogte'])
#    item42.text = (df.loc[row],['sakerendehoogte'])
#
#
## create a new XML file with the results
#mydata = ET.tostring(data2)
#myfile = open(input("XML opslaan als (zonder extentie): ")+".xml", "wb")
#myfile.write(mydata)
#myfile.close()
