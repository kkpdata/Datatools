#-------------------------------------------------------------------------------
# Name:        exportCSV
# Purpose:
#
# Author:      co
#
# Created:     14/10/2015
# Copyright:   (c) co 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# 20151028 CD changed sorting for Z-value in searchcursor

import os,sys

import locale
locale.setlocale(locale.LC_ALL,'')

import arcpy

sep = '\t'  # tab
sep = ';'
none = ''

#-------------------------------------------------------------------------------
def doAdd(fld):
#-------------------------------------------------------------------------------
    """
       returns true if field type not OID or geometry
    """
    if fld.type in ['OID',u'Geometry']:
        return False
    else:
        return True

#-------------------------------------------------------------------------------
def getFields(fc):
#-------------------------------------------------------------------------------
    """
        purpose: Make list of fields
    """
    # Created:     14/10/2015  co
    desc = arcpy.Describe(fc)
    flds = []
    for fld in  desc.Fields:
        if doAdd(fld):
            flds.append(fld)
    return flds


#-------------------------------------------------------------------------------
def getFieldsAsString(fc):
#-------------------------------------------------------------------------------
    """
        purpose: make header for csv
    """
    # Created:     14/10/2015  co

    sField = ''
    for fld in getFields(fc):
        sField += sep + fld.name
    sField = sField.strip(sep)
    return sField



#-------------------------------------------------------------------------------
def Log(message,status=0):
#-------------------------------------------------------------------------------
    """
       If status is 2 the exit
    """
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
def close(fo=None):
#-------------------------------------------------------------------------------
    """
        purpose: close file
    """
    # Created:     14/10/2015  co
    if fo:
        try:
            fo.close()
        except:
            pass




#-------------------------------------------------------------------------------
def main():
#-------------------------------------------------------------------------------
    try:
        # parameters
        if len(sys.argv) > 1:
            input = arcpy.GetParameterAsText(0)
            output = arcpy.GetParameterAsText(1)
        else:
            input = r'D:\projdata\gef\data\Sonderingen_Totaal4.gdb\sondering_lagen'
            output = r'D:\projdata\gef\data\csv'
            Log('Usage: exportCSV [featureclass/table]  [output CSV folder]')

        Log('Input: '+input)
        Log('Output: '+output)

        if not arcpy.Exists(input):
            Log('Input niet gevonden',2)

        fields = getFields(input)
        sFields = getFieldsAsString(input).upper()

        if not sFields.find('TESTID') >= 0 or not sFields.find('Z_NAP'):
            Log('Velden TESTID en/of Z_NAP niet gevonden',2)

        otestid = '#'
        fo = None
        # sorteren op TESTID en Z_NAP (omgekeerd van hoog naar laag wegschrijven)
        cur = arcpy.SearchCursor(input,None,None,None,'TESTID;Z_NAP D')
        for row in cur:
            testid = row.getValue('testid')
            if otestid <> testid:
                close(fo)
                otestid = testid
                fn = os.path.join(output,testid + '.csv')
                Log('Wegschrijven '+fn+' ...')
                fo = open(fn,'w')
                fo.write(sFields+'\n')
            sLine = ''
            for fld in fields:
                val = row.getValue(fld.name)
                if not val:
                    val = none
                if type(val) in [int,float]:
                    val = locale.str(val)
                if sLine:
                    sLine += sep + val
                else:
                    sLine = val
            fo.write(sLine+'\n')

        close(fo)  # close file with try-except catch
        del cur
        Log('Gereed!')



    except Exception,ErrorMsg:
        Log('Onverwachte fout in main(): '+str(ErrorMsg))

if __name__ == '__main__':
    main()
