#-------------------------------------------------------------------------------
# Name:        importGEF.py
# Purpose:
#
# Author:      co
#
# Created:     09/06/2015
# Copyright:   (c) co 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# 20160127 cd toegevoegd veld qq_n als Q_n

#from ConfigParser import *
import os,sys,fnmatch
import arcpy
import shutil


import gef
reload(gef)
NV = None
debug = True

from gef import *


fldsBoringen = [['FILENAME','text',50],['GEFID','text',10],['COMPANYID','text',10],['PROJECTID','text',10],['DATUM','text',10],
                ['TESTID','text',24],['RD_X','double',10,2],['RD_Y','double',10,2],['Z_NAP','double',8,2],['Opdrachtg','text',24],
                ['Norm','text',24],['Uitvoerder','text',24],['V_hor_niv','text',24],['Boormeth','text',24],
                ['Voorgegr_d','double',8,2],['GHG','double',8,2],['GLG','double',8,2],['Einddiepte','double',8,2],
                ['Grondws','double',8,2],['FILE_PATH','text',128]]


fldsBoringLagen = [['TESTID','text',15],['RD_X','double',10,2],['RD_Y','double',10,2],['Z_NAP','double',8,2],['ZT_MV','double',8,2],
                ['ZB_MV','double',8,2],['ZT_NAP','double',8,2],['ZB_NAP','double',8,2],['ZAND_MED','double',6,2],
                ['GRIND_MED','double',5,2],['LUTUM','double',5,2],['GRIND','double',5,2,],['ZAND','double',5,2],['OS','double',5,2],['GRONDSRT','text',10],
                ['TOEVOEG','text',15],['SOS_EENHEID','text',15],['gamma_sat','double',8,4],['u_0','double',8,4],['vert_gd_tot','double',8,4],['vert_gd_eff','double',8,4]
                ] # velden toegevoegd SOS_EENHEID is om een koppeling te maken met volumegewicht Deze volumegewichten staan in een aparte tabel (nog te maken)

fldsSonderingen = [['FILENAME','text',50],['GEFID','text',10],['COMPANYID','text',10],['PROJECTID','text',10],['DATUM','text',10],
                ['TESTID','text',24],['RD_X','double',10,2],['RD_Y','double',10,2],['Z_NAP','double',8,2],['Opdrachtg','text',35],
                ['NaamProj','text',35],['ConusType','text',24],['Norm','text',24],['V_hor_niv','text',24],
                ['Ontgr_dpte','double',8,2],['Grondws','double',8,2],['Einddiepte','double',8,2],['ConusFactA','double',8,2],['FILE_PATH','text',128]] # veld 'z_w' aangepast in 'Grondws'

fldsSonderingLagen = [['TESTID','text',15],['RD_X','double',10,2],['RD_Y','double',10,2],['Z_NAP','double',8,2],['sond_len','double',8,4],
                ['q_c','double',8,4],['wrijv_ws','double',8,4],['wrijv_get','double',8,4],['waterdr_u1','double',8,4],
                ['waterdr_u2','double',8,4],['waterdr_u3','double',8,4],['helling_rs','double',8,2],['helling_NS','double',8,4],['helling_EW','double',8,4],
                ['diepte_cor','double',8,4],['TIJD','double',8,4],['q_t','double',8,4,],['q_n','double',8,4],['qq_n','double',8,4],['Bq','double',8,4],['Nm','double',8,4],
                ['gamma_sat','double',8,4],['u_0','double',8,4],['vert_gd_tot','double',8,4],['vert_gd_eff','double',8,4], ['SOS_EENHEID','text',15]
				] # veld toegevoegd
                  # (cd) 20160127 qq_n toegevoegd als Q_n


#-------------------------------------------------------------------------------
def Log(message,status=0):
#-------------------------------------------------------------------------------
    try:
        print message
        if status == 0:
            arcpy.AddMessage(message)
        if status > 0:
            arcpy.AddWarning(message)
        if status < 0:
            arcpy.AddError(message)
            sys.exit(-1)
    except:
        print 'Fout in log'

#-------------------------------------------------------------------------------
def getlocal(vars,dr,fls):
#-------------------------------------------------------------------------------
    match = vars[0]
    for f in fls:
        if fnmatch.fnmatch(f,match):
            vars[1].append(os.path.join(dr,f))

#-------------------------------------------------------------------------------
def getAllFiles(basedir,match):
#-------------------------------------------------------------------------------
    if not os.path.isdir(basedir):
        return []
    sims = [match,[]]
    os.path.walk(basedir,getlocal,sims)
    return sims[1]

#-------------------------------------------------------------------------------
def DeleteObject(fc):
#-------------------------------------------------------------------------------
    """
        purpose:
    """
    # Created:     09/06/2015  co
    try:
        arcpy.Delete_management(fc)
    except:
        pass

#-------------------------------------------------------------------------------
def DeleteFolder(folder):
#-------------------------------------------------------------------------------
    """
        purpose:
    """
    # Created:     09/06/2015  co
    try:
        if os.path.isdir(folder):
            shutil.rmtree(folder,ignore_errors=False, onerror=None)
    except Exception, ErrorMsg:
        Log('Probleem met verwijderen folder ('+ folder + '): '+str(ErrorMsg))

#-------------------------------------------------------------------------------
def DeleteField(fc,fieldname):
#-------------------------------------------------------------------------------
    """
        purpose:
    """
    # Created:     09/06/2015  co
    try:
        arcpy.DeleteField_management(fc,fieldname)
    except:
        pass

#-------------------------------------------------------------------------------
def CreateFC(ws,fcnaam,featureType,fields):
#-------------------------------------------------------------------------------
    """
        purpose:
    """
    # Created:     09/06/2015  co
    try:
        fc = os.path.join(ws,fcnaam)
        if not arcpy.Exists(fc):
            Log('Aanmaken featureclass: '+fcnaam)
            arcpy.CreateFeatureclass_management(ws,fcnaam,featureType,None,'DISABLED','ENABLED')
            for fld in fields:
                if fld[1].lower() == 'text':
                    arcpy.AddField_management(fc,fld[0],'text',fld[2])
                elif fld[1] == 'double':
                    arcpy.AddField_management(fc,fld[0],'double',fld[2],fld[3])
                elif fld[1] == 'date':
                    arcpy.AddField_management(fc,fld[0],'date')
                else:
                    print fcnaam + ': Unknown field type: ' + fld[0] + '- ' + fld[1]
            DeleteField(fc,'id')
        else:
            Log('Toevoegen aan bestaande featureclass: '+fcnaam)
        return fc
    except Exception, ErrorMsg:
        Log('Onverwachte fout in CreateFC: '+str(ErrorMsg),-1)
        return None

#-------------------------------------------------------------------------------
def mFloat(val):
#-------------------------------------------------------------------------------
    try:
        return float(val)
    except:
        return None

#-------------------------------------------------------------------------------
def setValue(row,fieldname,val,fieldtype=None):
#-------------------------------------------------------------------------------
    """
        purpose:
    """
    # Created:     11/06/2015  co
    try:
        if val <> None:
            if fieldtype == 'float':
                val = float(val)
            elif fieldtype == 'int':
                val = int(val)
            row.setValue(fieldname,val)
        else:
            row.setValue(fieldname,NV)
    except:
        Log('Error setting field ' + fieldname + ' : '+str(val),1)


#-------------------------------------------------------------------------------
def writeBoring(fc,gefBoring):
#-------------------------------------------------------------------------------
    """
        purpose:
    """
    # Created:     21/06/2015  co
    cur = arcpy.InsertCursor(fc)
    row = cur.newRow()
    pt = arcpy.Point(gefBoring.X,gefBoring.Y,gefBoring.Z)
    setValue(row,'shape',pt)
    setValue(row,'filename',gefBoring.filename)
    setValue(row,'file_path',gefBoring.foldername)
    setValue(row,'GEFID',gefBoring.getHeaderValue('#GEFID'))
    setValue(row,'COMPANYID',gefBoring.getHeaderValue('#COMPANYID'))
    setValue(row,'PROJECTID',gefBoring.getHeaderValue('#PROJECTID'))
    setValue(row,'NORM',gefBoring.getHeaderValue('#MEASUREMENTCODE'))
    setValue(row,'TESTID',gefBoring.getHeaderValue('#TESTID'))
    setValue(row,'DATUM',gefBoring.MEASURES.getText(16))
    setValue(row,'RD_x',gefBoring.X)
    setValue(row,'RD_y',gefBoring.Y)
    setValue(row,'Z_NAP',gefBoring.Z)
    setValue(row,'uitvoerder',gefBoring.MEASURES.getText(13))
    setValue(row,'Opdrachtg',gefBoring.MEASURES.getText(1))
    setValue(row,'V_hor_niv',gefBoring.MEASURES.getText(9)) # vast horizontaal niveau
    setValue(row,'Boormeth',gefBoring.MEASURES.getText(31)) #boormethode
    setValue(row,'Voorgegr_d',gefBoring.MEASURES.getVar(13),'float') #voorgegraven diepte
    setValue(row,'GHG',gefBoring.MEASURES.getVar(14),'float')
    setValue(row,'GLG',gefBoring.MEASURES.getVar(15),'float')
    setValue(row,'Einddiepte',gefBoring.MEASURES.getVar(16),'float') # einddiepte
    setValue(row,'Grondws',gefBoring.MEASURES.getVar(18),'float') # einddiepte
    cur.insertRow(row)
    del row
    del cur


#-------------------------------------------------------------------------------
def writeBoringLaag(cur,TESTID,lyr):
#-------------------------------------------------------------------------------
    """
        purpose:
    """
    # Created:     21/06/2015  co
    row = cur.newRow()
    #lyr = BORING()
    pt = arcpy.Point(lyr.x,lyr.y,lyr.upperNAP)
    setValue(row,'shape',pt)
    setValue(row,'TESTID',TESTID)
    setValue(row,'GRONDSRT',lyr.grondsrt)
    setValue(row,'RD_X',lyr.x)
    setValue(row,'RD_Y',lyr.y)
    setValue(row,'Z_NAP',lyr.z)
    setValue(row,'ZT_MV',lyr.upper)
    setValue(row,'ZB_MV',lyr.lower)
    setValue(row,'ZT_NAP',lyr.upperNAP)
    setValue(row,'ZB_NAP',lyr.lowerNAP)
    setValue(row,'TOEVOEG',lyr.toevoegingen)
    setValue(row,'GRIND',lyr.grind)
    setValue(row,'ZAND_MED',lyr.zandmed)
    setValue(row,'GRIND_MED',lyr.grindmed)
    setValue(row,'ZAND',lyr.zand)
    setValue(row,'OS',lyr.os)
    setValue(row,'LUTUM',lyr.lutum)
    cur.insertRow(row)
    del row


#-------------------------------------------------------------------------------
def writeSondering(fc,gefS):
#-------------------------------------------------------------------------------
    """
        purpose:
    """
    # Created:     21/06/2015  co
    try:
        cur = arcpy.InsertCursor(fc)
        row = cur.newRow()
        pt = arcpy.Point(gefS.X,gefS.Y,gefS.Z)
        setValue(row,'shape',pt)
        setValue(row,'filename',gefS.filename)
        setValue(row,'file_path',gefS.foldername)
        setValue(row,'GEFID',gefS.getHeaderValue('#GEFID'))
        setValue(row,'COMPANYID',gefS.getHeaderValue('#COMPANYID'))
        setValue(row,'PROJECTID',gefS.getHeaderValue('#PROJECTID'))
        setValue(row,'TESTID',gefS.getHeaderValue('#TESTID'))
        setValue(row,'DATUM',gefS.getHeaderValue('#STARTDATE'))
        setValue(row,'RD_x',gefS.X)
        setValue(row,'RD_y',gefS.Y)
        setValue(row,'Z_NAP',gefS.Z)
        setValue(row,'Opdrachtg',gefS.MEASURES.getText(1))
        setValue(row,'NaamProj',gefS.MEASURES.getText(2))
        setValue(row,'ConusType',gefS.MEASURES.getText(4))
        setValue(row,'NORM',gefS.MEASURES.getText(6))
        setValue(row,'V_hor_niv',gefS.MEASURES.getText(9)) # vast horizontaal niveau
        setValue(row,'Ontgr_dpte',gefS.MEASURES.getVar(13), 'float') #voorgegraven diepte
        setValue(row,'Grondws',gefS.MEASURES.getVar(14),'float')  # z_w
        setValue(row,'Einddiepte',gefS.MEASURES.getVar(16),'float') # einddiepte
        setValue(row,'ConusFactA',gefS.MEASURES.getVar(3),'float') # einddiepte
        cur.insertRow(row)
        del row
        del cur
    except Exception,ErrorMsg:
        Log('Error in writeSondering: '+ str(ErrorMsg),1)

#-------------------------------------------------------------------------------
def writeSonderingLaag(cur,TESTID,lyr):
#-------------------------------------------------------------------------------
    """
        purpose:
    """
    # Created:     21/06/2015  co
    try:
        row = cur.newRow()
        #lyr = SONDERING()
        if lyr.diepteCor:
            z = lyr.z - lyr.diepteCor
        else:
            lyr.diepteCor = lyr.sondeerlengte  # indien geen diepte correctie dan diepte correctie is sondeerlengte
            z = lyr.z - lyr.sondeerlengte
        pt = arcpy.Point(lyr.x,lyr.y,z)
        setValue(row,'shape',pt)
        setValue(row,'TESTID',TESTID)
        setValue(row,'RD_X',lyr.x)
        setValue(row,'RD_Y',lyr.y)
        setValue(row,'Z_NAP',z)


        setValue(row,'sond_len',lyr.sondeerlengte)
        setValue(row,'diepte_cor',lyr.diepteCor)
        setValue(row,'q_c',lyr.q_c)
        setValue(row,'wrijv_ws',lyr.wrijvingsweerstand)
        setValue(row,'wrijv_get',lyr.wrijvingsgetal)

        setValue(row,'waterdr_u1',lyr.waterdruk_u1)
        setValue(row,'waterdr_u2',lyr.waterdruk_u2)
        setValue(row,'waterdr_u3',lyr.waterdruk_u3)

        setValue(row,'helling_rs',lyr.helling_resultante)
        setValue(row,'helling_ns',lyr.helling_NS)
        setValue(row,'helling_ew',lyr.helling_EW)

        setValue(row,'tijd',lyr.tijd)
        setValue(row,'q_t',lyr.q_t)
        setValue(row,'q_n',lyr.q_n)
        setValue(row,'BQ',lyr.Bq)
        setValue(row,'Nm',lyr.Nm)

        setValue(row,'u_0',lyr.u_0)
        setValue(row,'gamma_sat',lyr.gamma_sat)
        setValue(row,'q_t',lyr.q_t)
        setValue(row,'vert_gd_tot',lyr.vertGrondDruk_tot)
        setValue(row,'vert_gd_eff',lyr.vertGrondDruk_eff)


        cur.insertRow(row)
        del row
    except Exception,ErrorMsg:
        Log('Error in writeSonderingLaag: '+ str(ErrorMsg),1)

#-------------------------------------------------------------------------------
def doBoring(gefFile,fcb,fcbl):
#-------------------------------------------------------------------------------
    try:
        gf = GEF()
        gf.read(gefFile,'BORING')

        # writing boring to fc
        writeBoring(fcb,gf)

        # writing boring layers to fc
        cur = arcpy.InsertCursor(fcbl)
        for lyr in gf.layers:
            writeBoringLaag(cur,gf.TESTID,lyr)
        del cur
    except Exception, ErrorMsg:
        Log('Error in doBoringen: '+ str(ErrorMsg),1)


#-------------------------------------------------------------------------------
def doSondering(gefFile,fcb,fcbl):
#-------------------------------------------------------------------------------

    try:
        gf = GEF()
        gf.read(gefFile,'SONDERING')

        # writing sondering entry to fc
        writeSondering(fcb,gf)

        # writing sondering layers to fc
        cur = arcpy.InsertCursor(fcbl)
        for lyr in gf.layers:
            writeSonderingLaag(cur,gf.TESTID,lyr)
        del cur
    except Exception, ErrorMsg:
        Log('Error in doSondering: '+ str(ErrorMsg))


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if __name__ == '__main__':

    try:
        # parameters
        if len(sys.argv) > 1:
            folder = arcpy.GetParameterAsText(0)
            gefType = arcpy.GetParameterAsText(1).upper()
            outGDB = arcpy.GetParameterAsText(2)
        else:
            #boring voorbeeld
            gefType = "BORING"
            gefType = "SONDERING"
            if gefType == 'BORING':
                folder = r"D:\projdata\gef\voorbeelden\2_VoorbeeldBoringen\vanDINO"
                folder = r'D:\projdata\gef\source\20151008\data'
                folder = r'D:\projdata\gef\data\boring'
            else:
                folder = r'D:\projdata\gef\voorbeelden\1_VoorbeeldSonderingen\Van_DINO'
                folder = r'D:\projdata\gef\voorbeelden\1_VoorbeeldSonderingen\Van_Grondonderzoeksbureau'
                folder = r'D:\projdata\gef\source\test'
                folder = r'D:\projdata\gef\data\alles'

            outGDB = r'D:\projdata\gef\data\Sonderingen_Totaal4.gdb'
           # DeleteFolder(outGDB)

        gefFiles = getAllFiles(folder,'*.gef')
        if len(gefFiles) > 0:

            Log('Export maar FileGeodatabase '+outGDB)
            if not arcpy.Exists(outGDB):
                foldername = os.path.dirname(outGDB)
                fgdName = os.path.basename(outGDB)
                #arcpy.CreateFileGDB_management(foldername,fgdName,'9.3')
                arcpy.CreateFileGDB_management(foldername,fgdName)

            # Create featureclasses
            if gefType == "BORING":
                fcb = CreateFC(outGDB,'boringen','POINT',fldsBoringen)
                fcbl = CreateFC(outGDB,'boring_lagen','POINT',fldsBoringLagen) # deze stond verkeerd
            if gefType == "SONDERING":
                fcb = CreateFC(outGDB,'sonderingen','POINT',fldsSonderingen)
                fcbl = CreateFC(outGDB,'sondering_lagen','POINT',fldsSonderingLagen)


            i = 0
            for gefFile in gefFiles:
                i += 1
                Log('Verwerken '+gefFile+' ...')
                if gefType == "BORING":
                    doBoring(gefFile,fcb,fcbl)
                if gefType == "SONDERING":
                    doSondering(gefFile,fcb,fcbl)
            Log('Gereed met verwerken bestanden ('+str(i)+ ')')
        else:
            Log('Geen *.GEF bestanden gevonden in folder '+folder)
            sys.exit(-1)

    except Exception, ErrorMsg:
        Log('Error in __main__: '+ str(ErrorMsg))