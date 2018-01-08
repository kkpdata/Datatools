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

#include "cpdefinition.h"

CpDefinition::CpDefinition(const QString name, const bool mandatory, const int group_id)
    :CpDefinition(name, mandatory, group_id, 0)
{
}

CpDefinition::CpDefinition(const QString name, const bool mandatory, const int group_id, const int id)
{
    m_id = id;
    m_name = name;
    m_mandatory = mandatory;
    m_group_id = group_id;
}

QString CpDefinition::getName() const
{
    return m_name;
}

bool CpDefinition::isMandatory() const
{
    return m_mandatory;
}

int CpDefinition::getGroupId() const
{
    return m_group_id;
}

int CpDefinition::getId() const
{
    return m_id;
}

void CpDefinition::setId(int id)
{
    m_id = id;
}
