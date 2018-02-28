

import xml.etree.ElementTree as ET
import csv

data = ET.Element('configuratie')
with open(input("Bestandsnaam (zonder extentie): ")+".csv", 'r')as csvfile:
    cr = csv.DictReader(csvfile, delimiter=';')
    for row in cr:

        # create the file structure

        berekening = ET.SubElement(data, 'berekening')
        berekening.set('naam',row['berekeningnaam'])
        item1 = ET.SubElement(berekening, 'hrlocatie')
        item2 = ET.SubElement(berekening, 'kunstwerk')
        item3 = ET.SubElement(berekening, 'orientatie')
        item4 = ET.SubElement(berekening, 'faalkansgegevenerosiebodem')
        item8 = ET.SubElement(berekening, 'instroommodel')
        item6 = ET.SubElement(berekening, 'factorstormduur')
        item54 = ET.SubElement(berekening, 'nrdoorstroomopeningen')
        item55 = ET.SubElement(berekening, 'kansopopenstaan')
        item56 = ET.SubElement(berekening, 'kansmislukkensluiting')
        item7 = ET.SubElement(berekening, 'faalkansherstel')

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
        afvoercoefficient= ET.SubElement(stochasten,'stochast')
        afvoercoefficient.set('naam','afvoercoefficient')
        item33=ET.SubElement(afvoercoefficient,'verwachtingswaarde')
        binnenwaterstand= ET.SubElement(stochasten,'stochast')
        binnenwaterstand.set('naam','binnenwaterstand')
        item37=ET.SubElement(binnenwaterstand,'verwachtingswaarde')
        item38=ET.SubElement(binnenwaterstand, 'standaardafwijking')
        doorstroomoppervlak= ET.SubElement(stochasten,'stochast')
        doorstroomoppervlak.set('naam','doorstroomoppervlak')
        item25=ET.SubElement(doorstroomoppervlak,'verwachtingswaarde')
        item26=ET.SubElement(doorstroomoppervlak, 'standaardafwijking')
        drempelhoogte= ET.SubElement(stochasten,'stochast')
        drempelhoogte.set('naam','drempelhoogte')
        item51=ET.SubElement(drempelhoogte,'verwachtingswaarde')
        item52=ET.SubElement(drempelhoogte, 'standaardafwijking')
        kerendehoogte= ET.SubElement(stochasten,'stochast')
        kerendehoogte.set('naam','kruinhoogte')
        item41=ET.SubElement(kerendehoogte,'verwachtingswaarde')
        item42=ET.SubElement(kerendehoogte, 'standaardafwijking')
        item53= ET.SubElement(berekening, 'illustratiepunteninlezen')


        item1.text = row['hrlocatie']
        item2.text = row['kunstwerk']
        item3.text = row['orientatie']
        item4.text = row['faalkansgegevenerosiebodem']
        item6.text = row['factorstormduur']
        item7.text = row['faalkansherstel']
        item8.text = row['instroommodel']
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
        item33.text = row['afvoercoefficient']
        item37.text = row['binnenwaterstand']
        item38.text = row['sabinnenwaterstand']
        item41.text = row['kerendehoogte']
        item42.text = row['sakerendehoogte']
        item51.text = row['drempelhoogte']
        item52.text = row['sadrempelhoogte']
        item53.text = row['illustratiepunteninlezen']
        item54.text = row['nrdoorstroomopeningen']
        item55.text = row['kansopopenstaan']
        item56.text = row['kansmislukkensluiting']


# create a new XML file with the results
mydata = ET.tostring(data)
myfile = open(input("XML opslaan als (zonder extentie): ")+".xml", "wb")
myfile.write(mydata)
myfile.close()
