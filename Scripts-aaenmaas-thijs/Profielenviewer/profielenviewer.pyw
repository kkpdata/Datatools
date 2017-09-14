from __future__ import division
import math
import ttk
import xlrd
import csv
import os
import Tkconstants, tkFileDialog
import Tkinter as tk
import tkMessageBox as mbox
import numpy
import matplotlib
import traceback
from copy import deepcopy

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt

class Viewer(tk.Frame):

    #Initieer GUI
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.path = os.getcwd()
        
        #Menu bar
        self.menubar = tk.Menu(self)
        
        menu1 = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Menu", menu=menu1)
        menu1.add_command(label="Open .csv-bestand",command=self.open_file)
        menu1.add_command(label="Sla afbeelding op",command=self.save_image)
        menu1.add_command(label="Sluiten",command=self.rquit)

        menu2 = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Info", menu=menu2)
        menu2.add_command(label="Over de profielenviewer",command=self.popup)
        
        try:
            self.master.config(menu=self.menubar)
        except AttributeError:
            self.master.tk.call(master, "config", "-menu", self.menubar)
          

        #Progressbar
        self.pb_var = tk.IntVar(self)
        self.pb = ttk.Progressbar(self, orient="horizontal", length=100, mode="determinate", variable=self.pb_var, maximum=100000)
        
        #Listbox
        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.lb = tk.Listbox(self,selectmode=tk.EXTENDED,yscrollcommand=scrollbar.set)
        self.lb.config(width=25)
        self.lb.bind("<<ListboxSelect>>", self.onSelect)
        scrollbar.config(command=self.lb.yview)

        #Figure and canvas
        fig = matplotlib.figure.Figure(dpi=100,facecolor="white")
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.show()
        self.figSubPlot = self.canvas.figure.add_subplot(111)
        self.fig_settings()
        self.canvas.draw()

        #Entrise
        self.ex1 = tk.Entry(self, width=10)
        self.ex2 = tk.Entry(self, width=10)
        self.ey1 = tk.Entry(self, width=10)
        self.ey2 = tk.Entry(self, width=10)
        
        #Define positions in grid
        self.canvas.get_tk_widget().grid(   row=0,rowspan=6,column=2,               sticky=tk.W+tk.E+tk.N+tk.S)
        self.lb.grid(                       row=0,rowspan=4,column=0,               sticky=tk.W+tk.E+tk.N+tk.S)
        self.pb.grid(                       row=4,          column=0,columnspan=2,  sticky=tk.W+tk.E)
        scrollbar.grid(                     row=0,rowspan=5,column=1,               sticky=tk.W+tk.E+tk.N+tk.S)

        #Plot controls
        tk.Label(self, text="xmin:").grid(row=1, column = 3, sticky=tk.N)
        tk.Label(self, text="xmax:").grid(row=2, column = 3, sticky=tk.N)
        tk.Label(self, text="ymin:").grid(row=3, column = 3, sticky=tk.N)
        tk.Label(self, text="ymax:").grid(row=4, column = 3, sticky=tk.N)
        
        self.ex1.grid(row=1,column=4,sticky=tk.N)
        self.ex2.grid(row=2,column=4,sticky=tk.N)
        self.ey1.grid(row=3,column=4,sticky=tk.N)
        self.ey2.grid(row=4,column=4,sticky=tk.N)

        #Deze waarden geven aan welke rijen of kolommen onopgevulde ruimte moeten opvullen
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
       
        
    def popup(event):
        mbox.showinfo("Info", """De Profielenviewer is ontwikkeld binnen waterschap Aa en Maas om
te helpen bij bijvoorbeeld de vakindeling binnen de 4e beoordelingsronde van de primaire waterkering.

Voor vragen of opmerkingen kunt u contact opnemen met:
tijpelaar@aaenmaas.nl""")

    #Selecting items in the listbox
    def onSelect(self, val):
        sender = val.widget
        idx = sender.curselection()
        self.refreshFigure(idx)

    #Refresh the plots                                
    def refreshFigure(self,idx):
        self.canvas.figure.clf()
        self.figSubPlot = self.canvas.figure.add_subplot(111)

        #Set colormap
        jet = plt.get_cmap('winter') 
        cNorm  = matplotlib.colors.Normalize(vmin=0, vmax=len(idx))
        scalarMap = matplotlib.cm.ScalarMappable(norm=cNorm, cmap=jet)

        #Cycle through selected items and plot them
        a=0;
        for i in idx:
            j = self.keys[int(i)]
            x,y,z = self.dict[j]

            coords = zip(x,y)
            d=[0]
            for k in range(0,len(coords)-1):
                d.append(d[k] + distance(coords[k],coords[k+1]))

            colorVal = scalarMap.to_rgba(a)
            a=a+1
            self.figSubPlot.plot(d,z,color=colorVal)

        print d[-1]

        self.fig_settings()
        #self.ax.set_xlim(0, d[-1])
        
        self.ax.set_ylim(float(self.ey1.get()), float(self.ey2.get()))
        self.ax.set_xlim(float(self.ex1.get()), float(self.ex2.get()))
        
        self.canvas.draw()

    #Figuurinstellingen    
    def fig_settings(self):
        self.ax = self.canvas.figure.axes[0]
        self.ax.spines['left'].set_position('center')
        self.ax.set_title("Dwarsprofielen")
        self.ax.grid(True)
        self.ax.spines['right'].set_color('none')
        self.ax.spines['top'].set_color('none')      

    #Open a new file
    def open_file(self):
        self.lb.delete(0, tk.END)
        filename = tkFileDialog.askopenfilename(parent=root,initialdir=self.path,title='Selecteer profielenbestand')
        print filename
        if os.path.splitext(filename)[1]=='.csv':            
            try:
                self.dict = self.readcsv(filename)
                self.keys = self.dict.keys()
                self.keys.sort()
                for i in self.keys:
                    self.lb.insert(tk.END, i)
            except Exception as e: 
                #Reset progressbar
                print e
                traceback.print_exc()
                self.pb_var.set(0)
                mbox.showerror("Error","Fout bij het openen en inlezen van het bestand: "+str(e))

        else:
            mbox.showerror("Error","Het bestand dat u probeert te openen heeft niet de extensie 'csv'")

    #Read the CSV-file
    def readcsv(self,csvpath):
        #Reset progressbar
        self.pb_var.set(0)
        
        name=[];xcol=[];ycol=[];zcol=[]

        #Open excelfile
        with open(csvpath) as g:
            reader = csv.reader(g,delimiter=';')
            reader.next()
            self.update_progressbar(10000)
            for row in reader:
                xcol.append(float(row[2]))
                ycol.append(float(row[3]))
                zcol.append(float(row[4]))
                name.append(row[5])
        self.update_progressbar(10000)        
        xcol = numpy.array(xcol);ycol = numpy.array(ycol);zcol = numpy.array(zcol);name = numpy.array(name);
        self.update_progressbar(10000)

        zcol[zcol>999]  = None
        zcol[zcol<-999] = None
        zcol[zcol==0]   = None
      
        name_unique = set(name)

        #Cycle through all the profiles and define x, y and z values
        dict = {}
        dist = []
        len_profiel = 0 
        for n in name_unique:
            dict[n] = []
            index = numpy.where(name==n)[0]
            x = xcol[index]
            y = ycol[index]
            z = zcol[index]
            dict[n] = (x,y,z)
            self.update_progressbar(70000.0/len(name_unique))

            #sla afstanden eerste en laatste punt op voor xas
            dist.append(distance([x[0],y[0]], [x[-1],y[-1]]))

        
        #Vind maximale en minimale z-waarden
        self.zmax_init = max(zcol) * 1.25
        self.zmin_init = min(zcol) * 0.75

        #Vul de as-opties
        self.ey1.delete(0,tk.END),        self.ey1.insert(0,int(self.zmin_init))
        self.ey2.delete(0,tk.END),        self.ey2.insert(0,int(self.zmax_init))
        self.ex1.delete(0,tk.END),        self.ex1.insert(0,0)
        self.ex2.delete(0,tk.END),        self.ex2.insert(0,int(sum(dist)/len(dist)))

        #Maak de variabele aan die vanaf nu gebruikt wordt voor as-opties
        self.zmin = deepcopy(self.zmin_init)
        self.zmax = deepcopy(self.zmax_init)

        return dict

    #Save the current figure
    def save_image(self):
        filename = tkFileDialog.asksaveasfilename(parent=root,initialdir=self.path,title='Selecteer de locatie om het figuur op te slaan',defaultextension='.png')
        self.canvas.figure.savefig(filename)

    #Quit execution
    def rquit(self):
        root.destroy()

    #Update the progressbar
    def update_progressbar(self,val):
        self.pb_var.set( self.pb_var.get() + val)
        self.update_idletasks()


def distance(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)


if __name__ == '__main__':
    root = tk.Tk()
    Viewer(root).pack(side="top", fill="both", expand=True)
    root.geometry("1600x500")
    root.title("Profielenviewer")
    root.mainloop()

