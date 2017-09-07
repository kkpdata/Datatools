from __future__ import division
import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import re

def my_split(s):
    return filter(None, re.split(r'(\d+)', s))

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
folder = "input"
folder_son = "input_son"

#Robertson NL (FUGRO), handboring
basecolor = {'G': '#FFFFFF', 'K': '#C0FFC0', 'L': '#FFE9B9', 'V': '#DBAC63', 'Z': '#FFFF6E'}
subcolor  = {'s': '#FFA3A2', 'k': '#C0FFC0', 'z': '#FFFF6E'}
addcolor  = {'h': '#DBAC63', 'g': '#FFFFFF'}

#Robertson NL (FUGRO), sondering
color = ['white','#D13031','#D15F31','#006600','#B0E880','#DFF7B2','#FFE0B0','#FEB730','#D0C8CF','#D1D7E0','#808000']

n = 0
labels = []

#Maak een lijst van alle dijkpalen waar een handboring is
A = os.listdir(folder)
B = [p.split('+')[0].split('_')[2] for p in A]
C = list(set(B))

#Maak een lijst van alle dijkpalen waar een sondering is
As = os.listdir(folder_son)
Bs = [p.split('+')[0].split('_')[2] for p in As]

#Voor alle unieke waardes
for item in C:
    print item
    D =  [i for i,j in enumerate(B) if j == item]   #Index van handboringen bij deze dijkpaal
    Ds = [i for i,j in enumerate(Bs) if j == item]  #Index van sonderingen bij deze dijkpaal

    #set up axes
    fig = plt.figure()
    ax = fig.add_subplot(111)
    run = 1
    
    #Plot sondering:
    if len(Ds) == 1:
        file = As[Ds[0]]
        with open(os.path.join(folder_son,file)) as f:
            print f
            
            clas = []
            dept = []
                
            for line in f:
                if line.find("#ZID") > -1:
                    Z = map(float,line.split('=')[1].split(','))
                if line.find("Classificatie zone Robertson") > -1:
                    cc = int(line.split('=')[1].split(',')[0])
                if line.find("Gecorrigeerde diepte") > -1:
                    cd = int(line.split('=')[1].split(',')[0])
                    
                if line[0] != '#':
                    clas.append((line.split()[cc-1]))
                    dept.append((line.split()[cd-1]))

        depth = [Z[1] - float(x) for x in dept]
        d_top = depth[0:-1]
        d_bot = depth[1:]

        dijkpaal = file[9:12]
        labels.append(dijkpaal)
        
        for dt,db,c in zip(d_top,d_bot,clas):
            ax.add_patch(mpatches.Rectangle([2.5, db], 0.75, dt-db,linewidth=0,facecolor=color[int(c)]))

       
    #Plot handboring
    for index in D:
        file = A[index]
        print file
        
        if file.find('BITE') > 0:
            x = 4.5
        elif file.find('KR') > 0:
            x = 3.5
        elif file.find('BUTA') > 0:
            x = 1.5
        elif file.find('BUTE') > 0:
            x = 0.5
        else:
            print 'Geen bite, kr, buta or bute!'
            run = 0
            
        if run == 1:
            n = n+1
            with open(os.path.join(folder,file)) as f:

                print f
                clasf = []
                d_top = []
                d_bot = []
                            
                for line in f:
                    if line.find("#ZID") > -1:
                        Z = map(float,line.split('=')[1].split(','))
                    if line[0] != '#':
                        d_top.append(line.split(";")[0])
                        d_bot.append(line.split(";")[1])
                        clasf.append(line.split(";")[2].replace("'",""))
                
                dijkpaal = file[9:12]
                labels.append(dijkpaal)

                #Voor simplistische redenen uitgaan van een classificatie volgens NEN5104
                for dt,db,c in zip(d_top,d_bot,clasf):
                    csplit = []
                    #if statement omdat bij Gs, Zk en Vm geen nummer erna komt
                    if c[0:2] in ['Gs','Zk','Vm']:
                        csplit = [c[0:2],'6'] + my_split(c[2:])
                        print 'ja hoor'
                    else:
                        csplit = my_split(c)
                   
                    w = 0.75                    #profielbreedte
                    g = 15                      #factor sublagen t.o.v. basislaag
                    h = float(db)-float(dt)
                    l = 0
                    #x = float(dijkpaal)-(w/2)    
                    y = Z[1] - float(db)

                    #Basislaag plotten:
                    if csplit[0][0] in ['G', 'K', 'L', 'V', 'Z']:
                        ax.add_patch(mpatches.Rectangle([x,y],w ,h ,linewidth=0,facecolor=basecolor[csplit[0][0]]))
                    else:
                        print "Basislaag "+csplit[0][0]+"niet begrepen"

                    #siltige, zandige of kleiige toevoeging op de basislaag plotten:
                    if csplit[0][1]in ['z', 's', 'k']:
                        b = (int(csplit[1])/g) * w
                        l = l + b
                        xn = x+w-l
                        ax.add_patch(mpatches.Rectangle([xn,y],b ,h ,linewidth=0,facecolor=subcolor[csplit[0][1]]))
                        
                
                    #humus of grindlaag plotten:
                    if len(csplit) > 2:
                        if csplit[2] in ['h', 'g']:
                            b = (int(csplit[3])/g) * w
                            l = l + b
                            xn = x+w-l
                            ax.add_patch(mpatches.Rectangle([xn,y],b ,h ,linewidth=0,facecolor=addcolor[csplit[2]]))

                    if len(csplit) > 4:
                        if csplit[4] in ['h', 'g']:
                            b = (int(csplit[5])/g) * w
                            l = l + b
                            xn = x+w-l
                            ax.add_patch(mpatches.Rectangle([xn,y],b ,h ,linewidth=0,facecolor=addcolor[csplit[4]]))

    

    if run == 1:
          
        labels = ['', 'BUTE','BUTA','SON', 'KR','BITE']
        ax.set_xticklabels(labels)
        plt.ylim([0,14])
        plt.xlabel('Locatie')
        plt.xlim(0,6)
        plt.title(item)
        pp = PdfPages('output/'+str(item)+'.pdf')
        pp.savefig()
        pp.close()

        #plt.show()
        print "Klaar met "+str(item)

    #if run == 1:
    #    break

