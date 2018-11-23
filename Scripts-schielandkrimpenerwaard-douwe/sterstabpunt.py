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
            item44.text = row['voorlandprofiel']
        item5 = ET.SubElement(berekening, 'analysehoogte')
        item6 = ET.SubElement(berekening, 'factorstormduur')
        item7 = ET.SubElement(berekening, 'faalkansherstel')
        item8 = ET.SubElement(berekening, 'instroommodel')
        item9 = ET.SubElement(berekening, 'nrnivelleringen')
        item10= ET.SubElement(berekening, 'kansaanvaringtweedekeermiddel')
        item11= ET.SubElement(berekening, 'afstandonderkantwandteendijk')
        item12= ET.SubElement(berekening, 'volumiekgewichtwater')
            
        if vld:    
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
        doorstroomoppervlak= ET.SubElement(stochasten,'stochast')
        doorstroomoppervlak.set('naam','doorstroomoppervlak')
        item25=ET.SubElement(doorstroomoppervlak,'verwachtingswaarde')
        item26=ET.SubElement(doorstroomoppervlak, 'standaardafwijking')
        bermbreedte= ET.SubElement(stochasten,'stochast')
        bermbreedte.set('naam','bermbreedte')
        item27=ET.SubElement(bermbreedte,'verwachtingswaarde')
        item28=ET.SubElement(bermbreedte, 'standaardafwijking')
        lineairebelastingschematiseringsterkte= ET.SubElement(stochasten,'stochast')
        lineairebelastingschematiseringsterkte.set('naam','lineairebelastingschematiseringsterkte')
        item29=ET.SubElement(lineairebelastingschematiseringsterkte,'verwachtingswaarde')
        item30=ET.SubElement(lineairebelastingschematiseringsterkte, 'variatiecoefficient')
        kwadratischebelastingschematiseringsterkte= ET.SubElement(stochasten,'stochast')
        kwadratischebelastingschematiseringsterkte.set('naam','kwadratischebelastingschematiseringsterkte')
        item31=ET.SubElement(kwadratischebelastingschematiseringsterkte,'verwachtingswaarde')
        item32=ET.SubElement(kwadratischebelastingschematiseringsterkte, 'variatiecoefficient')
        afvoercoefficient= ET.SubElement(stochasten,'stochast')
        afvoercoefficient.set('naam','afvoercoefficient')
        item33=ET.SubElement(afvoercoefficient,'verwachtingswaarde')
        bezwijkwaardeaanvaarenergie= ET.SubElement(stochasten,'stochast')
        bezwijkwaardeaanvaarenergie.set('naam','bezwijkwaardeaanvaarenergie')
        item34=ET.SubElement(bezwijkwaardeaanvaarenergie,'verwachtingswaarde')
        item35=ET.SubElement(bezwijkwaardeaanvaarenergie, 'variatiecoefficient')
        kritiekestroomsnelheid= ET.SubElement(stochasten,'stochast')
        kritiekestroomsnelheid.set('naam','kritiekestroomsnelheid')
        item36=ET.SubElement(kritiekestroomsnelheid,'verwachtingswaarde')
        binnenwaterstand= ET.SubElement(stochasten,'stochast')
        binnenwaterstand.set('naam','binnenwaterstand')
        item37=ET.SubElement(binnenwaterstand,'verwachtingswaarde')
        item38=ET.SubElement(binnenwaterstand, 'standaardafwijking')
        binnenwaterstandbijfalen= ET.SubElement(stochasten,'stochast')
        binnenwaterstandbijfalen.set('naam','binnenwaterstandbijfalen')
        item39=ET.SubElement(binnenwaterstandbijfalen,'verwachtingswaarde')
        item40=ET.SubElement(binnenwaterstandbijfalen, 'standaardafwijking')
        kerendehoogte= ET.SubElement(stochasten,'stochast')
        kerendehoogte.set('naam','kerendehoogte')
        item41=ET.SubElement(kerendehoogte,'verwachtingswaarde')
        item42=ET.SubElement(kerendehoogte, 'standaardafwijking')
        massaschip= ET.SubElement(stochasten,'stochast')
        massaschip.set('naam','massaschip')
        item43=ET.SubElement(massaschip,'verwachtingswaarde')
        item44=ET.SubElement(massaschip, 'variatiecoefficient')
        aanvaarsnelheid= ET.SubElement(stochasten,'stochast')
        aanvaarsnelheid.set('naam','aanvaarsnelheid')
        item45=ET.SubElement(aanvaarsnelheid,'verwachtingswaarde')
        item46=ET.SubElement(aanvaarsnelheid, 'variatiecoefficient')
        lineairebelastingschematiseringstabiliteit= ET.SubElement(stochasten,'stochast')
        lineairebelastingschematiseringstabiliteit.set('naam','lineairebelastingschematiseringstabiliteit')
        item47=ET.SubElement(lineairebelastingschematiseringstabiliteit,'verwachtingswaarde')
        item48=ET.SubElement(lineairebelastingschematiseringstabiliteit, 'variatiecoefficient')
        kwadratischebelastingschematiseringstabiliteit= ET.SubElement(stochasten,'stochast')
        kwadratischebelastingschematiseringstabiliteit.set('naam','kwadratischebelastingschematiseringstabiliteit')
        item49=ET.SubElement(kwadratischebelastingschematiseringstabiliteit,'verwachtingswaarde')
        item50=ET.SubElement(kwadratischebelastingschematiseringstabiliteit, 'variatiecoefficient')
        drempelhoogte= ET.SubElement(stochasten,'stochast')
        drempelhoogte.set('naam','drempelhoogte')
        item51=ET.SubElement(drempelhoogte,'verwachtingswaarde')
        item52=ET.SubElement(drempelhoogte, 'standaardafwijking')
        item53= ET.SubElement(berekening, 'illustratiepunteninlezen')

        item1.text = row['hrlocatie']
        item2.text = row['kunstwerk']
        item3.text = row['orientatie']
        item4.text = row['faalkansgegevenerosiebodem']
        item5.text = row['analysehoogte']
        item6.text = row['factorstormduur']
        item7.text = row['faalkansherstel']
        item8.text = row['instroommodelsterstab']
        item9.text = row['nrnivelleringen']
        item10.text = row['kansaanvaringtweedekeermiddel']
        item11.text = row['afstandonderkantwandteendijk']
        item12.text = row['volumiekgewichtwater']
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
        item25.text = row['doorstroomoppervlak']
        item26.text = row['sadoorstroomoppervlak']
        item27.text = row['bermbreedte']
        item28.text = row['sabermbreedte']
        item29.text = row['lineairebelastingschematiseringsterkte']
        item30.text = row['vclineairebelastingschematiseringsterkte']
        item31.text = row['kwadratischebelastingschematiseringsterkte']
        item32.text = row['vckwadratischebelastingschematiseringsterkte']
        item33.text = row['afvoercoefficient']
        item34.text = row['bezwijkwaardeaanvaarenergie']
        item35.text = row['vcbezwijkwaardeaanvaarenergie']
        item36.text = row['kritiekestroomsnelheid']
        item37.text = row['binnenwaterstand']
        item38.text = row['sabinnenwaterstand']
        item39.text = row['binnenwaterstandbijfalen']
        item40.text = row['sabinnenwaterstandbijfalen']
        item41.text = row['kerendehoogte']
        item42.text = row['sakerendehoogte']
        item43.text = row['massaschip']
        item44.text = row['vcmassaschip']
        item45.text = row['aanvaarsnelheid']
        item46.text = row['vcaanvaarsnelheid']
        item47.text = row['lineairebelastingschematiseringstabiliteit']
        item48.text = row['vclineairebelastingschematiseringstabiliteit']
        item49.text = row['kwadratischebelastingschematiseringstabiliteit']
        item50.text = row['vckwadratischebelastingschematiseringstabiliteit']
        item51.text = row['drempelhoogte']
        item52.text = row['sadrempelhoogte']
        item53.text = row['illustratiepunteninlezen']



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
