# -*- coding: utf-8 -*-
'''
Thijs IJpelaar
tijpelaar@aaenmaas.nl
'''

from sys import exit
import numpy as np
from math import sqrt
from csv import reader
from ui import Ui_MainWindow
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QAction, QToolButton, QStyle

from matplotlib.pyplot import get_cmap
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable


from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT

class NavigationToolbar(NavigationToolbar2QT):
    '''Class that defines the toolbar
    Removes unnecessary buttons and adds a custom button
    Source: https://stackoverflow.com/questions/17711099/programmatically-change-matplotlib-toolbar-mode-in-qt4
    '''
    
    #Signal to redraw plot when legend is toggled
    legendSignal=pyqtSignal(int,name='legendSignal')
    #Signal to define axis limits when zoom/pan button is released
    viewChangeSignal=pyqtSignal(int,name='viewChangeSignal')
    
    def __init__(self, canvas, parent ):
        NavigationToolbar2QT.__init__(self,canvas,parent)
        self.showLegend = False
        
        # Search through existing buttons
        # next use for placement of custom button
        next=None
        for c in self.findChildren(QToolButton):
            if next is None:
                next=c
            #Verwijder buttons die we niet willen
            if str(c.text()) in ('Home','Customize','Forward','Back','Subplots'):
                c.defaultAction().setVisible(False)
                continue
            # Need to keep track of pan and zoom buttons
            if str(c.text()) in ('Pan','Zoom'):
                next=None
        
        #Define legend button
        legendButton=QAction("Toggle legend",self)
        legendButton.setIcon(QApplication.style().standardIcon(QStyle.SP_MessageBoxInformation))
        legendButton.setCheckable(True)
        legendButton.setToolTip("Toggle legend")
        self.legendButton = legendButton
        button=QToolButton(self)
        button.setDefaultAction(self.legendButton)

        #Add it to the toolbar, and connect up event
        self.insertWidget(next.defaultAction(),button)
        legendButton.toggled.connect(self.legendToggled)
        
        #Send a signal when the zoom or pan button is pressed.
        self.release_zoom('button_release_event')
        self.canvas.mpl_connect('button_release_event', self.viewChange)
        self.release_pan('button_release_event')
        self.canvas.mpl_connect('button_release_event', self.viewChange)      
    
    def viewChange(self, event):
        print('viewChange: zoom of pan button_release_event')
        self.viewChangeSignal.emit(1)
        
    def legendToggled(self, checked ):
        if self.legendButton.isChecked():
            self.showLegend = True
            print("legendToggled: legenda staat nu aan")
            self.legendSignal.emit(1)
        else:
            self.showLegend = False
            print("legendToggled: legenda staat nu uit")
            self.legendSignal.emit(1)

            
class mywindow(QMainWindow):
     
    def __init__(self): 
        super(mywindow, self).__init__() 
        self.ui = Ui_MainWindow()    
        self.ui.setupUi(self) 
        self.ui.statusbar.hide()
        self.justLoadedCsv = False
        
        #Menu items
        self.ui.actionExit.triggered.connect(self.close_application)
        self.ui.actionOpen_CSV.triggered.connect(self.openCsv)
        self.ui.actionAbout.triggered.connect(self.about)
   
        #Create figure object
        self.fig = Figure((8.0, 8.0), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.ui.gridLayout.addWidget(self.canvas, 1, 1, 2, 1)
        self.axes = self.fig.add_subplot(111)
        #self.canvas.setParent(self.ui.centralwidget)
        
        #Run function when figure gets updated
        self.fig.canvas.mpl_connect('draw_event', self.drawEvent)

        #Define toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.legendSignal.connect(self.graphicalSettings)
        self.toolbar.viewChangeSignal.connect(self.updateView)
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
           
        #Init graphicalSettings
        self.graphicalSettings()
        
        #Link selected profiles in the listWidget to the plotted profiles
        self.ui.listWidget.itemSelectionChanged.connect(self.updateProfiel)
        self.ui.statusbar.showMessage("De profielenviewer is opgestart, laadt een .csv-bestand in via het menu.")
        self.ui.progressBar.setValue(0)
                
    def updateView(self):
        '''Op het moment dat de toolbar het signaal viewChangeSignal stuurt, dus
        een van de buttons gebruikt wordt, zet dan deze flag updateView aan.
        
        Bij ieder draw event (dus wanneer de canvas wordt geupdated, wordt de functie
        drawEvent aangeroepen. Wanneer dit gebeurt nét na het loslaten van een knop,
        dus wanneer viewChangeSignal een signaal stuurt na een pan/ of zoomactie,
        dienen de axis-limits vastgezet te worden op deze nieuwe limieten'''
        
        print("updateView: updateView == 1")
        self.updateView = 1
        
    def drawEvent(self,event):
        #Update axis limits whenever the viewChangeSignal is sent
        if self.updateView == 1:
            self.xmin, self.xmax = self.axes.get_xlim()
            self.zmin, self.zmax = self.axes.get_ylim()
            print("drawEvent:",self.xmin,self.xmax,self.zmin,self.zmax)
            self.updateView = 0
        else:
            print("drawEvent: updateView == 0")
        
        #Make sure the axis limits remain untouched with regular draw actions
        self.updateView = 0
        
    def close_application(self):
        print("close_application: Profielenviewer sluit af")
        exit()

    def graphicalSettings(self):
        self.axes.spines['left'].set_position('center')
        self.axes.grid(True, which='both')
        self.axes.minorticks_on()
        self.axes.spines['right'].set_color('none')
        self.axes.spines['top'].set_color('none') 
        
        try: #If xmin is already defined
            print("graphicalSettings: updated axes limits", self.xmin,self.xmax)
            self.axes.set_xlim([self.xmin,self.xmax])
            self.axes.set_ylim([self.zmin,self.zmax])
        except Exception as e:
            print("graphicalSettings: cannot update axes limits",e)
        
        if self.toolbar.showLegend == True:
            print(self.axes.lines)
            if len(self.axes.lines) < 28: #If less then 24 items, only 1 column
                self.legend = self.axes.legend(loc='right',fontsize=8)
            else:
                self.legend = self.axes.legend(loc='right',fontsize=8, ncol = 2)
        else:
            try:
                self.legend.remove()
            except Exception as e: 
                print("graphicalSettings: cannot remove legend: "+str(e))

        self.fig.subplots_adjust(left=0.05,right=0.95,bottom=0.08,top=0.95)
        self.canvas.draw()
        
    def distance(self,p0, p1):
        return sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

    def openCsv(self):
        default_path = 'W:\WK\11. Persoonlijke Doc\9. Thijs\3. Scripts & Software\Python\Profielenviewer_QT'
        fname = QFileDialog.getOpenFileName(self, 'Open file', default_path,"CSV-bestanden (*.csv)")
        print(fname[0])
        try:
            self.dict = self.readCsv(fname[0])
            self.keys = self.dict.keys()
            self.keys = sorted(self.keys)
            self.keys = filter(None, self.keys) #Remove empty entry from list
            self.ui.listWidget.clear() 
            self.ui.listWidget.addItems(self.keys)
            
        except Exception as e: 
            self.displayError("openCsv: An error has occured: "+str(e))
            self.ui.progressBar.setValue(0)
            
    #Read the CSV-file
    def readCsv(self,fname):
        """Open and process the CSV-files
        
        Opent CSV-formaat surfaceslines voor zowel het DAM- als het RisKeer-
        formaat. Daar het DAM-formaat iets onhandiger in elkaar steekt
        vergt dit uiteindelijk iets meer processing.
        
        In de toekomst herschrijven naar of iets met pandas of een enkel script
        per type bestand.
        
        RisKeerformaat:
            LOCATIONID;X1;Y1;Z1;.....;Xn;Yn;Zn;(Profiel);;;;;;;;
        DAM-formaat:
            CODE;SUBCODE;X;Y;Z;RFLNAAM;DIJKPAAL;Afstand Profielpunten
        
        Args:
            fname (str): filename 
        """
        self.ui.progressBar.setValue(0)
        
        #Definieer wat variabelen
        i=0;j=0;d=[]
        dict = {}
        name=[];xcol=[];ycol=[];zcol=[]
        
        #Open csv-file
        with open(fname) as g:
            csvReader = reader(g,delimiter=';')
            self.ui.progressBar.setValue(10)
            for row in csvReader:
                
                #Bepaal in de eerste regel wat het formaat is van het bestand
                if i == 0: 
                    if row[0] == 'LOCATIONID': #Als het de input van QDamEdit betreft (RisKeer-formaat)
                        type_bestand = 'RisKeer'
                    else: #Als het de input van Dam Edit betreft (DAM-formaat)
                        type_bestand = 'DAM'
                        
                #Haal nu de x-, y- en z-waarden er uit
                else:
                    if type_bestand == 'DAM':
                        xcol.append(float(row[2]))
                        ycol.append(float(row[3]))
                        zcol.append(float(row[4]))
                        name.append(row[5])
                    elif type_bestand == 'RisKeer':
                        name = row[0]
                        x = [float(x) for x in row[1::3] if x]
                        y = [float(x) for x in row[2::3] if x]
                        z = [float(x) for x in row[3::3] if x]
                        zcol.extend(z) #Nodig voor definieren axis limits
                        x = np.array(x);y = np.array(y);z = np.array(z)
                        dict[name] = (x,y,z)
                        
                        #Calculate max distance for every 10th profile
                        if i%10 == 0:
                            coords = list(zip(x,y))
                            d.append(self.distance(coords[0],coords[-1]) )
                i=i+1

                
        #Postprocessing for DAM-files
        self.ui.progressBar.setValue(90)
        #Use Pandas dataframe?
        if type_bestand == 'DAM':
            xcol = np.array(xcol);ycol = np.array(ycol);zcol = np.array(zcol);name = np.array(name);
            zcol[zcol>999]  = None; zcol[zcol<-999] = None; zcol[zcol==0]   = None  
            name_unique = set(name)
            
            #Cycle through all the profiles and define x, y and z values
            for n in name_unique:
                #dict[n] = []
                index = np.where(name==n)[0]
                x = xcol[index]; y = ycol[index]; z = zcol[index]
                dict[n] = (x,y,z)
               # self.ui.progressBar.setValue(20 + 80/len(name_unique))
                
                #Calculate max distance for every 10th profile
                if j%10 == 0:
                    coords = list(zip(x,y))
                    d.append(self.distance(coords[0],coords[-1]) )
                j = j+1

        #Define axis limits. Dit moet hardcoded bij het inlezen van de CSV, na
        #aanpassen van de view met pan voor het inlezen van CSV zet het script ze
        #namelijk ook al vast.
        #Take the max occuring distance as the limit for the X-axis
        print("Distance:",d)
        self.xmin = 0        
        self.xmax = max(d)
        self.zmax = max(zcol) +2
        self.zmin = min(zcol) -2
        self.graphicalSettings()   
    
        print('csv goed ingelezen')
        self.ui.progressBar.setValue(100)

        return dict
        
    def updateProfiel(self):
        items = self.ui.listWidget.selectedItems()
        
        #Set colormap
        jet = get_cmap('winter') 
        cNorm  = Normalize(vmin=0, vmax=len(items))
        scalarMap = ScalarMappable(norm=cNorm, cmap=jet)
        
        a=0
        self.axes.clear()
        for profiel in [i.text() for i in items]:
            x,y,z = self.dict[profiel]
            coords = list(zip(x,y))
            d=[0]
            for k in range(0,len(coords)-1):
                d.append(d[k] + self.distance(coords[k],coords[k+1]))
            
            colorVal = scalarMap.to_rgba(a)
            a=a+1            
               
            self.axes.plot(d,z,color=colorVal, label=profiel)

        self.graphicalSettings()
        
    def displayError(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.exec_()
        
    def about(self):
        QMessageBox.about(self, "Profielenviewer 2.00",
"""De Profielenviewer is ontwikkeld binnen waterschap Aa en Maas. De tool is ontwikkeld in het kader van de 4e beoordelingsronde van de primaire  waterkering en heeft tot doel de meerdere dwarsprofielen van de waterkering tegelijkertijd te visualiseren.

Voor vragen of opmerkingen kunt u contact opnemen met:

tijpelaar@aaenmaas.nl""")
        
app = QApplication([])
application = mywindow()
application.show()
exit(app.exec())
