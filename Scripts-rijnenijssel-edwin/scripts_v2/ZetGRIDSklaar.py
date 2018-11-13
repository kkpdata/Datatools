# --------------------------------------------------------------------------
# Data voorbereiding per traject
# Witteveen+Bos
# ing. H.E.J. Nieuwland - februari 2018
# --------------------------------------------------------------------------
# versie 1.0.0
# --------------------------------------------------------------------------
# AHN, Flimap en RWS loading klaar zetten voor het betreffende traject
# --------------------------------------------------------------------------
import arcpy, string, os, sys

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = True
#---------------------------------------------------------
# INPUT
AHN        = sys.argv[1]      # Het AHN grid in m
Fmap       = sys.argv[2]      # Flimap
RWS        = sys.argv[3]      # RWS loadingen
MASK       = sys.argv[4]      # MASK            Dit is een buffer van de normtrajectlijn 200m buitenwaarts en 120m binnenwaarts
traj       = sys.argv[5]      # Trajectnummer
wdir       = sys.argv[6]      # De werkdirectorie
#---------------------------------------------------------
# ----  START
arcpy.AddMessage("\n>>  START  <<")
# min teken vervangen door undescore
traj = traj.replace("-","_")
arcpy.AddMessage("\n>> Traject:"+traj+" <<\n>>")
# workspace zetten.
arcpy.env.workspace = wdir
arcpy.env.cellSize = MASK
arcpy.env.extent = MASK
arcpy.env.mask = MASK
# AHN
arcpy.AddMessage("\n>> AHN knippen... <<\n>>")
arcpy.env.snapRaster = AHN                 
Guit = "AHN"+traj
sel = "\""+ AHN +"\""
arcpy.gp.RasterCalculator_sa(sel, Guit)
# Flimap
arcpy.AddMessage("\n>> Flimap knippen... <<\n>>")
arcpy.env.snapRaster = Fmap                 
Guit = "Flimap"+traj
sel = "\""+ Fmap +"\""
arcpy.gp.RasterCalculator_sa(sel, Guit)
# RWS loadingen
arcpy.AddMessage("\n>> RWS loadingen knippen... <<\n>>")
arcpy.env.snapRaster = AHN                 
Guit = "RWS"+traj
sel = "\""+ RWS +"\""
arcpy.gp.RasterCalculator_sa(sel, Guit)
#--                            
arcpy.AddMessage(">>---------------------------------------------------------------------------------------")
arcpy.AddMessage(">>---------------------------------------------------------------------------------------")
arcpy.AddMessage("\n>>>  KLAAR!  <<<")
