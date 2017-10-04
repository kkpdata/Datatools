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

#include "characteristicpoints.h"
#include "cpoint.h"

CharacteristicPoints* CharacteristicPoints::instance = nullptr;

CharacteristicPoints::CharacteristicPoints()
{
    m_next_id = CPOINT_ID_START;
    reset();
}

CharacteristicPoints::~CharacteristicPoints()
{
    clear();
    instance = nullptr;
}

// Singleton pattern. Return pointer to the one and only characteristic points object.
CharacteristicPoints *CharacteristicPoints::getInstance()
{
    if (!instance) instance = new CharacteristicPoints();
    return instance;
}

// Clear all definitions.
void CharacteristicPoints::clear()
{
    // Delete all cp_definitions
    foreach (CpDefinition* def, m_cp_definitions) {
        delete def;
    }
    m_cp_definitions.clear();
}

// Load standard definitions list.
void CharacteristicPoints::reset()
{
    clear();
    addCPointDefinition(new CpDefinition("Maaiveld buitenwaarts", true, 0, CPoint::MAAIVELD_BUITENWAARTS));
    addCPointDefinition(new CpDefinition("Teen geul", false, 11, CPoint::TEEN_GEUL));
    addCPointDefinition(new CpDefinition("Insteek geul", false, 11, CPoint::INSTEEK_GEUL));
    addCPointDefinition(new CpDefinition("Teen dijk buitenwaarts", true, 1, CPoint::TEEN_DIJK_BUITENWAARTS));
    addCPointDefinition(new CpDefinition("Kruin buitenberm", false, 12, CPoint::KRUIN_BUITENBERM));
    addCPointDefinition(new CpDefinition("Insteek buitenberm", false, 12, CPoint::INSTEEK_BUITENBERM));
    addCPointDefinition(new CpDefinition("Kruin buitentalud", true, 2, CPoint::KRUIN_BUITENTALUD));
    addCPointDefinition(new CpDefinition("Rand verkeersbelasting buitenwaarts", true, 15, CPoint::RAND_VERKEERSBELASTING_BUITENWAARTS));
    addCPointDefinition(new CpDefinition("Rand verkeersbelasting binnenwaarts", true, 15, CPoint::RAND_VERKEERSBELASTING_BINNENWAARTS));
    addCPointDefinition(new CpDefinition("Kruin binnentalud", true, 3, CPoint::KRUIN_BINNENTALUD));
    addCPointDefinition(new CpDefinition("Insteek binnenberm", false, 13, CPoint::INSTEEK_BINNENBERM));
    addCPointDefinition(new CpDefinition("Kruin binnenberm", false, 13, CPoint::KRUIN_BINNENBERM));
    addCPointDefinition(new CpDefinition("Teen dijk binnenwaarts", true, 4, CPoint::TEEN_DIJK_BINNENWAARTS));
    addCPointDefinition(new CpDefinition("Insteek sloot dijkzijde", false, 14, CPoint::INSTEEK_SLOOT_DIJKZIJDE));
    addCPointDefinition(new CpDefinition("Slootbodem dijkzijde", false, 14, CPoint::SLOOTBODEM_DIJKZIJDE));
    addCPointDefinition(new CpDefinition("Slootbodem polderzijde", false, 14, CPoint::SLOOTBODEM_POLDERZIJDE));
    addCPointDefinition(new CpDefinition("Insteek sloot polderzijde", false, 14, CPoint::INSTEEK_SLOOT_POLDERZIJDE));
    addCPointDefinition(new CpDefinition("Maaiveld binnenwaarts", true, 5, CPoint::MAAIVELD_BINNENWAARTS));
}

// Add a new characteristic point to the list of definitions.
int CharacteristicPoints::addCPointDefinition(CpDefinition *def)
{
    // Check if we already know the ID. If not, try to look it up and if it's not there, create a new ID.
    if (!def->getId()) {
        if (m_id_map.contains(def->getName())) {
            def->setId(m_id_map.value(def->getName()));
        } else {
            def->setId(m_next_id);
            m_next_id += CPOINT_ID_STEP;
            m_id_map.insert(def->getName(), def->getId());
        }
    } else {
        m_id_map.insert(def->getName(), def->getId());
    }

    // Add characteristic point definition to the map.
    m_cp_definitions.insert(def->getId(), def);
    return def->getId();
}

// Get characteristic point definition by its ID.
CpDefinition *CharacteristicPoints::lookupCPointDefinition(int id)
{
    return m_cp_definitions.value(id);
}

// Return a list of all characteristic point definitions.
QList<CpDefinition *> CharacteristicPoints::getCharacteristicPoints()
{
    return m_cp_definitions.values();
}
