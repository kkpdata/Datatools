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

#ifndef QCHARACTERISTICPOINTS_H
#define QCHARACTERISTICPOINTS_H

#include "cpdefinition.h"
#include <QMap>
#include <QList>


// This class contains the all the possible characteristic points in a project.
class CharacteristicPoints
{
public:
    // Each characteristic point has an ID. The ID can be given, but when not, the next available ID will be choosen.
    // In this case, the constants below define what the first ID is, and the step between two ID's.
    const int CPOINT_ID_START = 1000;
    const int CPOINT_ID_STEP  = 10;

    virtual ~CharacteristicPoints();
    static CharacteristicPoints* getInstance();

    // Delete all characteristic point definitions.
    void clear();

    // Load standard characteristic points.
    void reset();

    // add a new characteristic point definition to the list.
    // return its ID.
    int addCPointDefinition(CpDefinition* def);

    // lookup a characteristic point definition by its ID.
    CpDefinition* lookupCPointDefinition(int id);

    // Return a list with all characteristic points.
    QList<CpDefinition*> getCharacteristicPoints();

private:
    // Singleton, use getInstance().
    CharacteristicPoints();
    static CharacteristicPoints* instance;

    // The next available ID for a new characteristic point.
    int m_next_id;

    // This map contains all the possible characteristic points in this project.
    QMap<int, CpDefinition*> m_cp_definitions;

    // Lookup table to find the id which belongs to a name.
    QMap<QString, int> m_id_map;
};

#endif // QCHARACTERISTICPOINTS_H
