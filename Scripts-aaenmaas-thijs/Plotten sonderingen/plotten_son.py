import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

folder = "input"

fig1 = plt.figure(figsize=(20, 5), facecolor='w', edgecolor='k')
ax1 = fig1.add_subplot(111)

#Robertson NL (FUGRO)
color = ['white','#D13031','#D15F31','#006600','#B0E880','#DFF7B2','#FFE0B0','#FEB730','#D0C8CF','#D1D7E0','#808000']

n = 0
labels = []

for file in os.listdir(folder):
    n = n+1
    with open(os.path.join(folder,file)) as f:

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
        ax1.add_patch(mpatches.Rectangle([float(dijkpaal)-0.75, db], 1.5, dt-db,linewidth=0,facecolor=color[int(c)]))
    
#Unix:
labels = sorted(labels)

plt.grid()
plt.xlabel('dijkpaal [-]')
plt.ylabel('diepte [m+NAP]')
axes = plt.gca()
axes.set_xticks(range(0,1000,5))
axes.set_xlim([float(labels[0])-1,float(labels[-1])+1])
axes.set_ylim([-15,15])
axes.invert_xaxis()
#plt.show()
pp = PdfPages('profiel.pdf')
pp.savefig()
pp.close()
print "Klaar!" 
