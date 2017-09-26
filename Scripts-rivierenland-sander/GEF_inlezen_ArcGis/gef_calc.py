#-------------------------------------------------------------------------------
# Name:        gef_calc.py
# Purpose:     import koppetabel en berekenen verticale gronddruk en u_0
#
# Author:      co
#
# Created:     11-01-2016
# Copyright:   (c) co 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os,sys

import arcpy

EXIT = True
gravity = 9.81 #Bij boringen moet de waterdruk in kPa

#-------------------------------------------------------------------------------
def log(msg,exit=False):
#-------------------------------------------------------------------------------
    """
        purpose:
    """
    # Created:     11-01-2016  co
    print msg
    if exit:
        arcpy.AddError(msg)
        sys.exit(-1)
    else:
        arcpy.AddMessage(msg)


#-------------------------------------------------------------------------------
def quote(string):
#-------------------------------------------------------------------------------
    """
        purpose:
    """
    # Created:     11-01-2016  co
    res = string.strip("'")
    return "'" + res + "'"




#-------------------------------------------------------------------------------
def getFields(table):
#-------------------------------------------------------------------------------
    """
        purpose:
    """
    # Created:     11-01-2016  co
    try:
        desc = arcpy.Describe(table)
        fields = desc.fields
        flds = []
        for fld in desc.fields:
            flds.append(fld.name.upper())
        return flds
    except Exception,ErrorMsg:
        log('ERROR: (getFields): '+str(ErrorMsg),EXIT)



class KoppelTabel:

    #-------------------------------------------------------------------------------
    def __init__(self):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     11-01-2016  co
        self.rows = []
        self.fields = []


    #-------------------------------------------------------------------------------
    def readTable(self,koppeltabel):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     11-01-2016  co

        # fields
        self.fields = getFields(koppeltabel)
        # remove OID
        desc = arcpy.Describe(koppeltabel)
        fldOID = desc.OIDFieldName
        self.fields.remove(fldOID)
        # read  records
        cur = arcpy.SearchCursor(koppeltabel)
        for row in cur:
            elem = {}
            for fld in self.fields:
                elem[fld] = row.getValue(fld)
            self.rows.append(elem)
        del cur

    #-------------------------------------------------------------------------------
    def getElem(self,TESTID,ZT_MV,ZB=None):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     11-01-2016  co
        testid = TESTID.upper()
        if not ZB:
            ZB_MV = ZT_MV
        else:
            ZB_MV = ZB
        for row in self.rows:
            if row['TESTID'].upper() == testid:
                row_ZT_MV = row['ZT_MV']
                row_ZB_MV = row['ZB_MV']
                if ZT_MV >= row_ZT_MV and ZB_MV <= row_ZB_MV:
                    return row


#-------------------------------------------------------------------------------
class Boringen:
#-------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------
    def __init__(self):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     11-01-2016  co
        self.fields = []
        self.rows = []
        pass

    #-------------------------------------------------------------------------------
    def koppelLayers(self,fcBoringen,koppeltabel):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     11-01-2016  co
        desc = arcpy.Describe(fcBoringen)
        fldOID = desc.OIDFieldName
        self.fields = getFields(fcBoringen)
        cur = arcpy.UpdateCursor(fcBoringen)
        for elem in cur:
            oid = elem.getValue(fldOID)
            testid = elem.getValue('TESTID')
            zt_mv = elem.getValue('ZT_MV')
            zb_mv = elem.getValue('ZB_MV')
            koppel = koppeltabel.getElem(testid,zt_mv,zb_mv)
            if koppel:
                #log('Rij %i (%s,%8.2f,%8.2f) : gekoppeld' % (oid,testid,zt_mv,zb_mv))
                for f in koppel:
                    if f not in ('TESTID','ZT_MV','ZB_MV'):
                        if f in self.fields:
                            elem.setValue(f,koppel[f])
                        else:
                            log('* %s: veld %s niet in lagen tabel' % (testid,f))
                cur.updateRow(elem)
            else:
                log('*Rij %i (%s,%8.2f,%8.2f) : niet gekoppeld' % (oid,testid,zt_mv,zb_mv))
        del cur

    #-------------------------------------------------------------------------------
    def calculate(self,fcBoringen,fcBoringLagen):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     11-01-2016  co
        try:
            curB = arcpy.SearchCursor(fcBoringen)
            for rowB in curB:
                testid = rowB.getValue('TESTID')
                z_nap = rowB.getValue('Z_NAP')
                z_w = rowB.getValue('GRONDWS')
                log('Berekenen %s:' % (testid))
                if not z_nap:
                    log('  *geen Z_NAP')
                if not z_w:
                    log('  *geen GRONDWS(z_w)')
                if z_nap and z_w:
                    if z_w > z_nap:
                        log('  *GRONDWS(z_w) > Z_NAP  %f > %f >> u_0=0' % (z_w,z_nap))
                        #z_w = z_nap
                    curL = arcpy.UpdateCursor(fcBoringLagen,'TESTID='+quote(testid),None,'','ZT_MV')
                    vert_sum = 0
                    bSum = True
                    for rowL in curL:
                        zt_mv = rowL.getValue('ZT_MV')
                        zb_mv = rowL.getValue('ZB_MV')
                        #Berekening van u_0
                        if zb_mv > z_w:
                            u_0 = gravity * (zb_mv - z_w)
                        else:
                            u_0 = 0.0
                        #u_0 wegschrijven
                        rowL.setValue('U_0',u_0)
                        gamma_sat = rowL.getValue('GAMMA_SAT')
                        if not gamma_sat:
                            bSum = false
                            log('  *geen gamma_sat (%f-%f) (berekening is niet mogelijk)' % (zt_mv,zb_mv))
                        else:
                            if bSum:
                                vert_druk = (zb_mv - zt_mv) * gamma_sat
                                vert_sum += vert_druk
                                rowL.setValue('VERT_GD_TOT',vert_sum)
                                rowL.setValue('VERT_GD_EFF',vert_sum-u_0)
                                log('  %5.2f-%5.2f  - %8.2f %8.2f' % (zt_mv,zb_mv,vert_sum,vert_sum-u_0))
                        curL.updateRow(rowL)
                    del curL

            del curB

        except Exception, ErrorMsg:
            log('ERROR (Boringen.calculate): ' + str(ErrorMsg),EXIT)


#-------------------------------------------------------------------------------
class Sonderingen:
#-------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------
    def __init__(self):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     11-01-2016  co
        self.fields = []
        self.rows = []
        pass

    #-------------------------------------------------------------------------------
    def koppelLayers(self,fcSonderingen,koppeltabel):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     11-01-2016  co
        desc = arcpy.Describe(fcSonderingen)
        fldOID = desc.OIDFieldName
        self.fields = getFields(fcSonderingen)
        cur = arcpy.UpdateCursor(fcSonderingen)
        for elem in cur:
            oid = elem.getValue(fldOID)
            testid = elem.getValue('TESTID')
            diepte_cor = elem.getValue('DIEPTE_COR')

            koppel = koppeltabel.getElem(testid,diepte_cor)
            if koppel:
                #log('Rij %i (%s,%8.2f,%8.2f) : gekoppeld' % (oid,testid,zt_mv,zb_mv))
                for f in koppel:
                    if f not in ('TESTID','ZT_MV','ZB_MV'):
                        if f in self.fields:
                            elem.setValue(f,koppel[f])
                        else:
                            log('* %s: veld %s niet in lagen tabel' % (testid,f))
                cur.updateRow(elem)
            else:
                log('*Rij %i (%s,%8.2f,%8.2f) : niet gekoppeld' % (oid,testid,zt_mv,zb_mv))
        del cur

    #-------------------------------------------------------------------------------
    def calculate(self,fcSonderingen,fcSonderingLagen):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     11-01-2016  co
        try:
            curB = arcpy.SearchCursor(fcSonderingen)
            for rowB in curB:
                testid = rowB.getValue('TESTID')
                z_nap = rowB.getValue('Z_NAP')
                z_w = rowB.getValue('GRONDWS')
                a = rowB.getValue('CONUSFACTA')
                if not a:
                    log(' *geen conusfactor')
                else:
                    log (' conus factor (a): %f' % (a))
                log('Berekenen %s:' % (testid))
                if not z_nap:
                    log('  *geen Z_NAP')
                if not z_w:
                    log('  *geen GRONDWS(z_w)')
                if z_nap and z_w:
                    if z_w > z_nap:
                        log('  *GRONDWS(z_w) > Z_NAP  %f > %f >> u_0=0' % (z_w,z_nap))
                        #z_w = z_nap
                    curL = arcpy.UpdateCursor(fcSonderingLagen,'TESTID='+quote(testid),None,'','DIEPTE_COR')
                    vert_sum = 0
                    log('  %5s  - %12s %12s %12s %12s' % ('diepte','vert_druk','druk_sum','druk_eff','u_0'))
                    voorgaande_diepte = '#'
                    bSum = True
                    for rowL in curL:
                        diepte = rowL.getValue('DIEPTE_COR')
                        #diepte vorige rij bewaren
                        if voorgaande_diepte == '#':
                            voorgaande_diepte = diepte
                            continue
                        q_c = rowL.getValue('Q_C')
                        u2 = rowL.getValue('WATERDR_U2')
                        q_t = rowL.getValue('Q_T')
                        if not q_c:
                            log(' *qc = None: stel qc=0')
                            q_c = 0.0
                        if not u2:
                            log(' *u2 = None: stel u2=0')
                            u2 = 0.0
                        if not q_t:
                            log(' *q_t = None: stel q_t=0')
                            q_t = 0.0
                        #Berekening van u_0
                        if diepte > z_w:
                            u0 = gravity * (diepte - z_w)
                        else:
                            u0 = 0.0
                        #u_0 wegschrijven
                        rowL.setValue('U_0',u0)
                        gamma_sat = rowL.getValue('GAMMA_SAT')

                        if not gamma_sat:
                            bSum = false
                            log('  *geen gamma_sat (%f) (berekening is niet mogelijk)' % (diepte))
                        else:
                            if bSum:
                                vert_druk = (diepte - voorgaande_diepte) * gamma_sat
                                # de laag druk sommeren voor de laag er onder
                                vert_sum += vert_druk

                                vert_eff = vert_sum-u0
                                rowL.setValue('VERT_GD_TOT',vert_sum)
                                rowL.setValue('VERT_GD_EFF',vert_eff)

                                if a:
                                    #q_t = q_c + (u2*(1-a)) #q_t wordt al berekend in gef.py
                                    #rowL.setValue('Q_T',q_t)
                                    q_n = 0.0
                                    if q_t <> 0.0:
                                        q_n = (q_t * 1000.0) - vert_sum #q_n in kPa
                                    rowL.setValue('Q_N',q_n)
                                    if vert_sum <> 0 and q_n <> 0: # niet delen door 0
                                        qq_n = q_n / vert_sum
                                        try:
                                            rowL.setValue('QQ_N',qq_n)
                                        except:
                                            log('  probleem met toevoegen Q_N (waarschijnlijk bestaat veld niet) (Sonderingen.calculate)')
                                    bq = 0
                                    if q_n <> 0.0 and u2:
                                        bq = (u2-u0) / q_n
                                    rowL.setValue('BQ',bq)
                                    log('  %5.2f  - %12.2f %12.2f %12.2f %12.2f' % (diepte,vert_druk,vert_sum,vert_eff,u0))



                        # voorgaande rij updaten
                        voorgaande_diepte = diepte
                        curL.updateRow(rowL)

                    del curL

            del curB

        except Exception, ErrorMsg:
            log('ERROR (Sonderingen.calculate): ' + str(ErrorMsg),EXIT)

    #-------------------------------------------------------------------------------
    def calculate_test(self,fcSonderingen,fcSonderingLagen):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     11-01-2016  co
        try:
            curB = arcpy.SearchCursor(fcSonderingen)
            for rowB in curB:
                testid = rowB.getValue('TESTID')
                z_nap = rowB.getValue('Z_NAP')
                z_w = rowB.getValue('GRONDWS')
                a = rowB.getValue('CONUSFACTA')
                if not a:
                    log(' *geen conusfactor')
                else:
                    log (' conus factor (a): %f' % (a))
                log('Berekenen %s:' % (testid))
                if not z_nap:
                    log('  *geen Z_NAP')
                if not z_w:
                    log('  *geen GRONDWS(z_w)')
                if z_nap and z_w:
                    if z_w > z_nap:
                        log('  *GRONDWS(z_w) > Z_NAP  %f > %f >> u_0=0' % (z_w,z_nap))
                        #z_w = z_nap
                    curL = arcpy.UpdateCursor(fcSonderingLagen,'TESTID='+quote(testid),None,'','DIEPTE_COR')
                    vert_sum = 0
                    lagen = []
                    log('  %5s  - %12s %12s %12s %12s' % ('diepte','vert_druk','druk_sum','druk_eff','u_0'))
                    voorgaande_diepte = '#'
                    bSum = True
                    i = 0
                    for rowL in curL:
                        diepte = rowL.getValue('DIEPTE_COR')
                        #diepte vorige rij bewaren
                        if voorgaande_diepte == '#':
                            bBereken = False
                            voorgaande_diepte = diepte
                            if diepte > 0:   #voorgeboorde diepte
                                gamma_sat = rowL.getValue('GAMMA_SAT')
                                if gamma_sat:
                                    bBereken = True
                                    vert_sum = diepte * gamma_sat
                                    lagen.append([diepte,vert_sum,vert_sum,0,0])
                            if not bBereken:
                                lagen.append([diepte,0,0,0,0,0])
                            continue
                        q_c = rowL.getValue('Q_C')
                        u2 = rowL.getValue('WATERDR_U2')
                        q_t = rowL.getValue('Q_T')
                        if not q_c:
                            log(' *qc = None: stel qc=0')
                            q_c = 0.0
                        if not u2:
                            log(' *u2 = None: stel u2=0')
                            u2 = 0.0
                        if not q_t:
                            log(' *q_t = None: stel q_t=0')
                            q_t = 0.0
                        #Berekening van u_0
                        if diepte > z_w:
                            u0 = gravity * (diepte - z_w)
                        else:
                            u0 = 0.0
                        #u_0 wegschrijven
                        rowL.setValue('U_0',u0)
                        gamma_sat = rowL.getValue('GAMMA_SAT')

                        if not gamma_sat:
                            bSum = false
                            log('  *geen gamma_sat (%f) (berekening is niet mogelijk)' % (diepte))
                            lagen.append([diepte,0.0,0.0,u0,0.0])
                        else:
                            if bSum:
                                vert_druk = (diepte - voorgaande_diepte) * gamma_sat
                                vert_sum += vert_druk
                                vert_eff = vert_sum-u0
                                ##rowL.setValue('VERT_GD_TOT',vert_sum)
                                ##rowL.setValue('VERT_GD_EFF',vert_eff)
                                q_n = 0.0
                                if a:
                                    #q_t = q_c + (u2*(1-a)) #q_t wordt al berekend in gef.py
                                    #rowL.setValue('Q_T',q_t)
                                    if q_t <> 0.0:
                                        q_n = (q_t * 1000.0) - vert_sum #q_n in kPa
                                    rowL.setValue('Q_N',q_n)

                                    if vert_sum <> 0 and q_n <> 0: # niet delen door 0
                                        qq_n = q_n / vert_sum
                                        try:
                                            rowL.setValue('QQ_N',qq_n)
                                        except:
                                            log('  probleem met toevoegen Q_N (waarschijnlijk bestaat veld niet) (Sonderingen.calculate)')
                                    bq = 0
                                    if q_n <> 0.0 and u2:
                                        bq = (u2-u0) / q_n
                                    rowL.setValue('BQ',bq)
                                lagen.append([diepte,vert_druk,vert_sum,u0,q_n])
                            else:
                                print 'raar'

                        # voorgaande rij updaten
                        voorgaande_diepte = diepte
                        curL.updateRow(rowL)
                        i += 1
                    del curL
                    # sum 1 laag opschuiven naar beneden....loop de cursor nog een keer door
                    i = 0
                    curL = arcpy.UpdateCursor(fcSonderingLagen,'TESTID='+quote(testid),None,'','DIEPTE_COR')
                    for rowL in curL:
                        if lagen[i]:
                            diepte = lagen[i][0]
                            if (i+1) >= len(lagen):
                                vert_sum = lagen[i][2]
                            else:
                                vert_sum = lagen[i+1][2]
                            u0 = lagen[i][3]
                            vert_eff = vert_sum - u0
                            q_n = lagen[i][4]
                            qq_n = 0.0
                            if vert_sum <> 0:
                                qq_n = q_n / vert_sum
                            rowL.setValue('VERT_GD_TOT',vert_sum)
                            rowL.setValue('VERT_GD_EFF',vert_eff)
                            rowL.setValue('QQ_N',qq_n)
                            log('  %5.2f  - %12.3f %12.3f %12.3f %12.3f' % (diepte,vert_druk,vert_sum,vert_eff,u0))
                        i += 1

                    del curL

            del curB

        except Exception, ErrorMsg:
            log('ERROR (Sonderingen.calculate): ' + str(ErrorMsg),EXIT)


def main():

    try:
        # parameters
        if len(sys.argv) > 1:
            log('Inlezen parameters...')
            gefType = arcpy.GetParameterAsText(0).upper()
            GDB = arcpy.GetParameterAsText(1)
            tabKoppelTabel = arcpy.GetParameterAsText(2)
        else:
            #gefType = "BORING"
            #tabKoppelTabel = r'C:\temp\TestKoppelenGrndSrt.gdb\Koppeltabel'
            #GDB =  r'C:\temp\TestKoppelenGrndSrt.gdb'
			gefType = "SONDERING"
			tabKoppelTabel = r'D:\projdata\gef\data\TestKoppelenGrndSrt.gdb\Koppeltabel'
			GDB = r'D:\projdata\gef\data\TestKoppelenGrndSrt.gdb'

        if gefType == "BORING":
            fcObjecten = os.path.join(GDB,'boringen')
            fcObjectLagen = os.path.join(GDB,'boring_lagen')
        elif gefType == "SONDERING":
            fcObjecten = os.path.join(GDB,'sonderingen')
            fcObjectLagen = os.path.join(GDB,'sondering_lagen')
        else:
            log('Onbekend GEF type (BORING/SONDERING): '+gefType,EXIT)

        # inlezen koppeltabel
        log('Inlezen koppeltabel...')
        koppel = KoppelTabel()
        koppel.readTable(tabKoppelTabel)

        if gefType == "BORING":
            lagen = Boringen()
            log('Verwerken koppeltabel...')
            lagen.koppelLayers(fcObjectLagen,koppel)
            log('Uitvoeren berekeningen...')
            lagen.calculate(fcObjecten,fcObjectLagen)
        elif gefType == "SONDERING":
            lagen = Sonderingen()
            log('Verwerken koppeltabel...')
            lagen.koppelLayers(fcObjectLagen,koppel)
            log('Uitvoeren berekeningen...')
            lagen.calculate(fcObjecten,fcObjectLagen)
        else:
            log('Onbekend GEF type')

        log('Gereed')
    except Exception, ErrorMsg:
            log('ERROR (gef_calc.main): ' + str(ErrorMsg),EXIT)

if __name__ == '__main__':
    main()

