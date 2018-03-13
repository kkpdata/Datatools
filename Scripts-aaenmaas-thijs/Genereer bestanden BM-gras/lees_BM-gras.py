# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 09:13:25 2017

@author: Thijs IJPelaar

Dit script leest de safetyfactors uit berekende BM-grasdocumenten uit
"""

import xml.etree.cElementTree as ET
import os

#Aan te passen pad, selecteer de folder met de uitgerekende BM-grasbestanden
dir = r'\\tsclient\W\WB\1. Toetssporen\36-1\6. GEBU\6. Projectbestanden BM Gras'

with open('output.csv', 'w') as f:
    for xml in os.listdir(dir):
        tree = ET.ElementTree(file=os.path.join(dir,xml))
        for output in tree.iter(tag='Output'):
            if output.attrib['Key'] == '14':
                f.write(str(xml)+';'+str(output.attrib['FoS'])+'\n')
                print(xml,output.attrib['FoS'])
