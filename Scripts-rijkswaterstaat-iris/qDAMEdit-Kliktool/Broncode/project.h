/**********************************************************************
* This file is part of qDAMEdit.
*
* qDAMEdit is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* qDAMEdit is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with qDAMEdit.  If not, see <http://www.gnu.org/licenses/>.
*
* qDAMEdit is written in Qt version 5.9.
*
* Copyright 2017 TWISQ (http://www.twisq.nl)
***********************************************************************/

#ifndef PROJECT_H
#define PROJECT_H

#include <QList>
#include <QMap>
#include <QTextStream>

#include "crosssection.h"
#include "cpdefinition.h"

class Project
{
public:
    Project();
    virtual ~Project();

    QList<Crosssection*> getCrosssections() {return m_crosssections;}
    int numCrosssections() {return m_crosssections.count();}

    int getCurrent_crosssection_index() const;
    void setCurrent_crosssection_index(int current_crosssection_index);

    void setTrafficloadOffset(const double offset) {m_trafficload_offset = offset;}
    double getTrafficloadOffset() {return m_trafficload_offset;}

    bool getRecording() const;
    void setRecording(bool value);

    bool isDirty() const;
    void setDirty(const bool d);

    Crosssection* getCrosssection(const int index);
    Crosssection* getCrosssection(const QString label);
    Crosssection* getCurrentCrosssection();

    void addCharacteristicPointToCurrentCrosssection(CPoint* point);

    CpDefinition *getCurrentCpDefinition() const;
    CpDefinition *getCpDefinitionByID(const int id);
    void setCurrentCpDefinition(CpDefinition *current_cpoint_definition);
    bool gotoNextCPoint();

    // FILE READ WRITE FUNCTIONS

    bool readCsv(QTextStream& stream);
    bool readDatabase(QTextStream& stream);

    bool writeSurfacelines(QTextStream& stream);
    bool writeCharacteristicpoints(QTextStream& stream);
    bool writeLog(QTextStream& stream);
    bool writeDatabase(QTextStream& stream);

    // When an error occurs during read/write, the reason can be found in this string.
    QString getReadWriteErrorMsg();

private:
    QList<Crosssection*> m_crosssections;
    double m_trafficload_offset;
    CpDefinition* m_current_cpoint_definition;
    int m_current_crosssection_index;
    bool m_recording;   // True if user has clicked the record button.
    bool m_dirty;       // True if cpoints have been changed and not saved yet.
    QString m_readWriteErrorMsg;

    void clearData();
    bool readSurface(QTextStream& stream);
    bool readAlternativeSurface(QTextStream& stream);
    bool readCharacteristicpoints(QTextStream& stream, QString header);
    bool readLog(QTextStream& stream);
};

#endif // PROJECT_H
