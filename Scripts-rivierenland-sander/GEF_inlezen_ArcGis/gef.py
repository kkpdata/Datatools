#-------------------------------------------------------------------------------
# Name:        gef2shp.py
# Purpose:     Reading FEF file to export to ArcGIS Featureclass
#
# Author:      Co Drost - GISwerk 2015
#
# Created:     08/06/2015
# Copyright:   (c) co 2015
# Licence:     -
#-------------------------------------------------------------------------------

import os,sys,re

# module re used for string matching/extract in decodeLayer string

NOVALUE = -9999

#-------------------------------------------------------------------------------
def decodeLayers(string,rec_sep='!',col_sep=';'):
#-------------------------------------------------------------------------------
    """
        purpose:
    """
    # Created:     09/06/2015  co
    res = []
    if not rec_sep:
        rec_sep = '\n'
    if not col_sep:
        col_sep = ' '
    lst = string.split(rec_sep)
    for elem in lst:
        elem = elem.strip()
        if len(elem) > 0:
            if col_sep == ' ':
                rec = re.split(r"\s{1,}",elem)
            else:
                rec = elem.split(col_sep)
            res.append(rec)
    return res

#-------------------------------------------------------------------------------
def unquote(string):
#-------------------------------------------------------------------------------
    return string.strip("'")

#-------------------------------------------------------------------------------
def concat(lst,conchar=' '):
#-------------------------------------------------------------------------------
    """
      merges a list to a string
    """
    res = ''
    for elem in lst:
        res += conchar + unquote(elem)
    return res.strip(conchar)

#-------------------------------------------------------------------------------
class LAYERS:
#-------------------------------------------------------------------------------
    """
        purpose:
    """
    # Created:     21/06/2015  co

    #-------------------------------------------------------------------------------
    def __init__(self,parent):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     21/06/2015  co
        self.parent = parent
        self.columns = parent.COLUMNS
        self.columnsNum = None
        self.columnsVoids = None
        self.x,self.y,self.z = parent.X,parent.Y,parent.Z
        self.layers = []
        self.type = 'UNKNOWN'


    #-------------------------------------------------------------------------------
    def __len__(self):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     21/06/2015  co
        return len(self.layers)

    #-------------------------------------------------------------------------------
    def __getitem__(self,n):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     21/06/2015  co
        try:
            return self.layers[n]
        except:
            raise IndexError

    #-------------------------------------------------------------------------------
    def getValue(self,nr,lst,tp='TEXT'):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     21/06/2015  co
        try:
            if self.columnsNum[nr]:
                i = self.columnsNum[nr]
                vd = self.columnsVoids[nr]
                val = lst[i-1]
                if val == vd:
                    return None
                else:
                    if tp == 'FLOAT':
                        return float(val)
                    elif tp == 'LONG':
                        return int(val)
                    else:
                        return val
            return None
        except:
            return None

#-------------------------------------------------------------------------------
class BORING:
#-------------------------------------------------------------------------------
    """
        class comment
    """

    def __init__(self,x,y,z,upper,lower,zandmed,grindmed,lutum,silt,zand,grind,os,grondsrt,toevoegingen):
        self.x = x
        self.y = y
        self.z = z
        self.upper = upper
        self.lower = lower
        self.zandmed = zandmed
        self.grindmed = grindmed
        self.lutum = lutum
        self.silt = silt
        self.zand = zand
        self.grind = grind
        self.os = os
        self.grondsrt = grondsrt
        self.toevoegingen = toevoegingen


    #-------------------------------------------------------------------------------
    @property
    def upperNAP(self):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     15/06/2015  co
        return self.z - self.upper

    #-------------------------------------------------------------------------------
    @property
    def lowerNAP(self):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     15/06/2015  co
        return self.z - self.lower

#-------------------------------------------------------------------------------
class BORINGEN(LAYERS):
#-------------------------------------------------------------------------------
    """
        purpose:
    """
    # Created:     21/06/2015  co

    #-------------------------------------------------------------------------------
    def __init__(self,parent):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     21/06/2015  co
        LAYERS.__init__(self,parent)
        self.columnsNum = self.columns.columnsByID(1,2,8,9,3,4,5,6,7)
        self.columnsVoids = self.columns.voidsByID(1,2,8,9,3,4,5,6,7)



    #-------------------------------------------------------------------------------
    def getValue(self,nr,lst,tp='TEXT'):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     21/06/2015  co
        try:
            if self.columnsNum[nr]:
                i = self.columnsNum[nr]
                vd = self.columnsVoids[nr]
                val = lst[i-1]
                if val == vd:
                    return None
                else:
                    if tp == 'FLOAT':
                        return float(val)
                    elif tp == 'LONG':
                        return int(val)
                    else:
                        return val
            return None
        except:
            return None


    #-------------------------------------------------------------------------------
    def add(self,lstOfElements):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     21/06/2015  co
        lst = lstOfElements
        top = self.getValue(0,lst,'FLOAT')
        bottom = self.getValue(1,lst,'FLOAT')
        zandmed = self.getValue(2,lst,'FLOAT')
        grindmed = self.getValue(3,lst,'FLOAT')
        lutum = self.getValue(4,lst,'FLOAT')
        silt = self.getValue(5,lst,'FLOAT')
        zand = self.getValue(6,lst,'FLOAT')
        grind = self.getValue(7,lst,'FLOAT')
        os = self.getValue(8,lst,'FLOAT')
        grondsoort = ''
        toevoegingen = ''
        if len(self.columns) < len(lst):
            grondsoort = unquote(lst[len(self.columns)])
        if len(self.columns) + 1 < len(lst):
            toevoegingen = concat(lst[len(self.columns)+1:])

        boring = BORING(self.x,self.y,self.z,top,bottom,zandmed,grindmed,lutum,silt,zand,grind,os,grondsoort,toevoegingen)
        self.layers.append(boring)
        #lsty,z,upper,lower,zandmed,grindmed,lutum,silt,zand,grind,os,grondsrt,toevoegingen):


#-------------------------------------------------------------------------------
class SONDERING(object):
#-------------------------------------------------------------------------------
    """
        class comment
    """

    def __init__(self,x,y,z,sondeerlengte,q_c,wrijvingsweerstand,wrijvingsgetal,waterdruk_u1,waterdruk_u2,waterdruk_u3,helling_resultante,helling_NS,helling_EW,diepteCor,tijd,q_t,q_n,Bq,Nm,gamma_sat,u_0,vertGrondDruk_tot,vertGrondDruk_eff):
        self.x = x
        self.y = y
        self.z = z
        self.sondeerlengte = sondeerlengte
        self.q_c = q_c
        self.wrijvingsweerstand = wrijvingsweerstand
        self.wrijvingsgetal = wrijvingsgetal
        self.waterdruk_u1 = waterdruk_u1
        self.waterdruk_u2 = waterdruk_u2
        self.waterdruk_u3 = waterdruk_u3
        self.helling_resultante = helling_resultante
        self.helling_NS = helling_NS
        self.helling_EW = helling_EW
        self.diepteCor = diepteCor
        self.tijd = tijd
        self.q_t = q_t
        self.q_n = q_n
        self.Bq = Bq
        self.Nm = Nm
        self.gamma_sat = gamma_sat
        self.u_0 = u_0
        self.vertGrondDruk_tot = vertGrondDruk_tot
        self.vertGrondDruk_eff = vertGrondDruk_eff


#-------------------------------------------------------------------------------
class SONDERINGEN(LAYERS):
#-------------------------------------------------------------------------------
    """
        purpose:
    """
    # Created:     21/06/2015  co

    #-------------------------------------------------------------------------------
    def __init__(self,parent):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     21/06/2015  co
        LAYERS.__init__(self,parent)
        self.columnsNum = self.columns.columnsByID(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20)
        self.columnsVoids = self.columns.voidsByID(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20)



    #-------------------------------------------------------------------------------
    def getValue(self,nr,lst,tp='TEXT'):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     21/06/2015  co
        try:
            if self.columnsNum[nr]:
                i = self.columnsNum[nr]
                vd = self.columnsVoids[nr]
                if not vd:
                    vd = '-9999.00000'
                val = lst[i-1]
                if val == vd:
                    return None
                else:
                    if tp == 'FLOAT':
                        val = float(val)
                        if val <> float(vd):
                            return float(val)
                        else:
                            return None
                    elif tp == 'LONG':
                        return int(val)
                    else:
                        return val
            return None
        except:
            return None


    #-------------------------------------------------------------------------------
    def add(self,lstOfElements):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     21/06/2015  co
        lst = lstOfElements
        sondeerlengte = self.getValue(0,lst,'FLOAT')
        q_c = self.getValue(1,lst,'FLOAT')
        wrijvingsweerstand = self.getValue(2,lst,'FLOAT')
        wrijvingsgetal = self.getValue(3,lst,'FLOAT')
        waterdruk_u1 = self.getValue(4,lst,'FLOAT')
        waterdruk_u2 = self.getValue(5,lst,'FLOAT')
        waterdruk_u3 = self.getValue(6,lst,'FLOAT')
        helling_resultante = self.getValue(7,lst,'FLOAT')
        helling_NS = self.getValue(8,lst,'FLOAT')
        helling_EW = self.getValue(9,lst,'FLOAT')
        diepteCor = self.getValue(10,lst,'FLOAT')
        tijd = self.getValue(11,lst,'FLOAT')
        q_t =self.getValue(12,lst,'FLOAT')
        q_n = self.getValue(13,lst,'FLOAT')
        Bq = self.getValue(14,lst,'FLOAT')
        Nm = self.getValue(15,lst,'FLOAT')
        gamma_sat = self.getValue(16,lst,'FLOAT')
        u_0 = self.getValue(17,lst,'FLOAT')
        vertGrondDruk_tot = self.getValue(18,lst,'FLOAT')
        vertGrondDruk_eff = self.getValue(19,lst,'FLOAT')

        if not diepteCor:
            diepteCor = sondeerlengte

        # berekening van de statistische waterdruk. Als diepteCor < z_w dan u_0 = 0.0
        z_w = self.parent.MEASURES.getVar(14)  #grondws in kPa
        if not u_0:
            if z_w:
                z_w = float(z_w)
                if diepteCor > z_w:
                    u_0 = 9.81 * (diepteCor - z_w)
                else:
                    u_0 = 0.0
        
        # haal a uit GEF, zoniet gebruik van 0.75 (standaardwaarde)
        a = self.parent.MEASURES.getVar(3)  #Netto oppervlaktequotient van de conuspunt
        if not a:
            a = 0.75
        else:
            a = float(a)
        
        # Berekening q_t

        if not q_t:
            if q_c and waterdruk_u2:
                q_t = q_c + (waterdruk_u2 * (1 -a))

        if not q_n:
            if q_t and vertGrondDruk_tot:
                q_n = q_t - vertGrondDruk_tot

        if not Bq:
            if waterdruk_u2 and u_0 and q_n:
                if q_n <> 0:
                    Bq = (waterdruk_u2 - u_0) / q_n


        sondering = SONDERING(self.x,self.y,self.z,sondeerlengte,q_c,wrijvingsweerstand,wrijvingsgetal,waterdruk_u1,waterdruk_u2,waterdruk_u3,helling_resultante,helling_NS,helling_EW,diepteCor,tijd,q_t,q_n,Bq,Nm,gamma_sat,u_0,vertGrondDruk_tot,vertGrondDruk_eff)
        self.layers.append(sondering)

#-------------------------------------------------------------------------------
class COLUMN():
#-------------------------------------------------------------------------------
    """
        class comment
    """

    def __init__(self,nr=None,units=None,description=None,id=None,void=None):
        self.nr = int(nr)
        self.units = units
        self.description = description
        self.id = int(id)
        self.void = void

    #-------------------------------------------------------------------------------
    def __str__(self):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     08/06/2015  co
        return '%2i : %5s, %30s, %3i %10s' % (self.nr,self.units,self.description,self.id,self.void)

#-------------------------------------------------------------------------------
class COLUMNS:

    #-------------------------------------------------------------------------------
    def __init__(self):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     08/06/2015  co
        self.columns = {}
        self.__index = {}

    #-------------------------------------------------------------------------------
    def readColumnInfo(self,content):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     08/06/2015  co
        try:
            content = content.strip()
            elems = content.split(',')
            colnr = int(elems[0].strip())
            colunits = elems[1].strip()
            coldesc = elems[2].strip()
            colid = int(elems[3].strip())
            if self.columns.has_key(colnr):
                col = self.columns[colnr]
                col.units = colunits
                col.description = coldesc
                col.id = colid
            else:
                self.columns[colnr] = COLUMN(colnr,colunits,coldesc,colid)
        except Exception, ErrorMsg:
            print 'readColumnInfo: '+ str(ErrorMsg)

    #-------------------------------------------------------------------------------
    def readColumnVoid(self,content):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     08/06/2015  co
        try:
            content = content.strip()
            elems = content.split(',')
            colnr = int(elems[0].strip())
            void = elems[1].strip()

            if self.columns.has_key(colnr):
                col = self.columns[colnr]
                col.void = void
            else:
                self.columns[colnr] = COLUMN(colnr,None,None,None,void)
        except Exception, ErrorMsg:
            print 'readColumnInfo: '+ str(ErrorMsg)

    #-------------------------------------------------------------------------------
    def __str__(self):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     08/06/2015  co
        res = ''
        for colnr in self.columns:
            col = self.columns[colnr]
            res += str(col) + '\n'
        return res

    #-------------------------------------------------------------------------------
    def index(self,id):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     11/06/2015  co
        if self.__index:
            if self.__index.has_key(id):
                return self.__index[id]
            else:
                return None
        # if no index then create __index
        for colnr in self.columns:
            self.__index[self.columns[colnr].id] = colnr
        if self.__index.has_key(id):
            return self.__index[id]
        else:
            return None

    #-------------------------------------------------------------------------------
    def columnsByID(self,*columns):
    #-------------------------------------------------------------------------------
        try:
            res = []
            for id in list(columns):
                res.append(self.index(id))
            return res
        except Exception, ErrorMsg:
            print ErrorMsg
            return []

    #-------------------------------------------------------------------------------
    def voidsByID(self,*columns):
    #-------------------------------------------------------------------------------
        try:
            res = []
            for id in list(columns):
                index = self.index(id)
                if index:
                    void = self.columns[index].void
                else:
                    void = None
                res.append(void)
            return res
        except Exception, ErrorMsg:
            print ErrorMsg
            return []



    #-------------------------------------------------------------------------------
    def __len__(self):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     08/06/2015  co
        return len(self.columns)

    #-------------------------------------------------------------------------------
    def __getitem__(self,i):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     11/06/2015  co
        try:
            return self.columns[i]
        except Exception, ErrorMsg:
            return None


#-------------------------------------------------------------------------------
class MEASUREMENTS():
    """
        class comment
    """

    def __init__(self):
        self.measurementsText = {}
        self.measurementsVar = {}


    #-------------------------------------------------------------------------------
    def readText(self,contents):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     09/06/2015  co
        try:
            res = contents.strip().split(',')
            if len(res) > 3:
                res2 = res[-1]
                res0 = res[0]
                res1 = contents.strip().split(',',1)[1]
                res1 = res1[:len(res1)-len(res2)].strip(' ,')
                self.measurementsText[int(res0)] = [res1,res2.strip()]
            else:
                self.measurementsText[int(res[0])] = [res[1].strip(),res[2].strip()]
        except Exception, ErrorMsg:
            print ErrorMsg

    #-------------------------------------------------------------------------------
    def readVar(self,contents):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     09/06/2015  co
        try:
            res = contents.strip().split(',')
            self.measurementsVar[int(res[0])] = [res[1].strip(),res[2].strip(),res[3].strip()]
        except Exception, ErrorMsg:
            print ErrorMsg


    #-------------------------------------------------------------------------------
    def getText(self,nr):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     09/06/2015  co
        if self.measurementsText.has_key(nr):
            return unquote(self.measurementsText[nr][0])
        else:
            return None


    #-------------------------------------------------------------------------------
    def getVar(self,nr):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     09/06/2015  co
        if self.measurementsVar.has_key(nr):
            return self.measurementsVar[nr][0]
        else:
            return None



#-------------------------------------------------------------------------------
class GEF:

    #-------------------------------------------------------------------------------
    def __init__(self):
    #-------------------------------------------------------------------------------
        """
            purpose: defining class
        """
        # Created:     08/06/2015  co
        self.GEFID = None
        self.COLUMNTEXT = None
        self.COLUMNS = COLUMNS()
        self.HEADER = {}
        self.MEASURES = MEASUREMENTS()
        self.layers = []
        self.X,self.Y,self.Z = 0,0,0
    #-------------------------------------------------------------------------------
    def readBoring(self,filename):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     15/06/2015  co
        self.read(filename,'BORING')


    #-------------------------------------------------------------------------------
    def readSondering(self,filename):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     15/06/2015  co
        self.read(filename,'SONDERING')

    #-------------------------------------------------------------------------------
    def read(self,filename,geftype="BORING"):
    #-------------------------------------------------------------------------------
        """
            purpose: reading GEF file into object
        """
        # Created:     08/06/2015  co

        try:
            self.HEADER = {}
            self.COLUMNS = COLUMNS()
            self.filename = os.path.basename(filename)
            self.foldername = os.path.abspath(filename)
            fi = open(filename,'r')
            lines = fi.readlines()
            fi.close()
            for line in lines:
                line = line.strip(' \n')
                if line:
                    if line[0] == '#':
                        ln = line.split('=')
                        tag = ln[0].strip(' ')
                        if tag == '#COLUMNINFO':
                            self.COLUMNS.readColumnInfo(ln[1])
                        if tag == '#COLUMNVOID':
                            self.COLUMNS.readColumnVoid(ln[1])
                        if tag == '#MEASUREMENTTEXT':
                            self.MEASURES.readText(ln[1])
                        if tag == '#MEASUREMENTVAR':
                            self.MEASURES.readVar(ln[1])
                        else:
                            self.HEADER[tag] = ln[1].strip(' ')
            bEOH = False
            self.X,self.Y,self.Z = self.getXYZ()
            sLayers = ''
            rec_sep = self.getHeaderValue('#RECORDSEPARATOR')
            for line in lines:
                if rec_sep:
                    line = line.strip('\n')
                if line.split('=')[0].strip() == '#EOH':
                    bEOH = True
                if bEOH and line[0] <> '#':
                    sLayers+= line
            res = decodeLayers(sLayers,rec_sep,self.getHeaderValue('#COLUMNSEPARATOR'),)
            if geftype == 'BORING':
                self.layers = BORINGEN(self)
                for lyr in res:
                    self.layers.add(lyr)
            elif geftype == 'SONDERING':
                self.layers = SONDERINGEN(self)
                for lyr in res:
                    self.layers.add(lyr)
                #self.layers = BORINGEN(self.X,self.Y,self.Z,self.COLUMNS)
                #self.layers.add(lyr)

        except Exception, ErrorMsg:
            print ErrorMsg
            return False

    #-------------------------------------------------------------------------------
    def getHeaderValue(self,tag):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     09/06/2015  co
        if self.HEADER.has_key(tag):
            return self.HEADER[tag]
        else:
            return None

    #-------------------------------------------------------------------------------
    @property
    def TESTID(self):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     09/06/2015  co
        return self.getHeaderValue('#TESTID')

    #-------------------------------------------------------------------------------
    def getXYZ(self):
    #-------------------------------------------------------------------------------
        """
            purpose: get surface location x,y,z
        """
        # Created:     09/06/2015  co
        res = self.getHeaderValue('#XYID').split(',')
        x,y = res[1],res[2]
        res =  self.getHeaderValue('#ZID').split(',')
        z = res[1]
        return float(x),float(y),float(z)


    #-------------------------------------------------------------------------------
    def layerInfo(self,n,code):
    #-------------------------------------------------------------------------------
        """
            purpose: get n-th line dor specific code
        """
        # Created:     11/06/2015  co
        c = self.COLUMNS.index(code)
        if c:
            val = self.LAYERS[n][c-1]
            if val == self.COLUMNS[c].void:
                return None
            return val
        else:
            return None

    #-------------------------------------------------------------------------------
    def layerInfoRest(self,n,i):
    #-------------------------------------------------------------------------------
        """
            purpose:
        """
        # Created:     11/06/2015  co
        try:
            cols = len(self.COLUMNS)
            val = self.LAYERS[n][cols-1+i]
            return val.strip("'" )
        except Exception, ErrorMsg:
            print ErrorMsg
            return None








def main():
    gef = GEF()
    #gef.read('..\data\B39D2633_dino.gef','BORING')
    gef.read('../data/S39A00340.gef','SONDERING')
    #print gef.HEADER
    #print gef.COLUMNS
    #print len(gef.LAYERS.layers)


if __name__ == '__main__':
    pass
    #main()


