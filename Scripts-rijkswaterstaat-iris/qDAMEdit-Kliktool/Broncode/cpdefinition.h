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

#ifndef CPDEFINITION_H
#define CPDEFINITION_H

#include <QString>

// Name, id and other definition data of characteristic points.
class CpDefinition
{
public:
    CpDefinition(const QString name, const bool mandatory, const int group_id);
    CpDefinition(const QString name, const bool mandatory, const int group_id, const int id);

    QString getName() const;
    bool isMandatory() const;
    int getGroupId() const;
    int getId() const;
    void setId(int id);

private:
    QString m_name;
    bool m_mandatory;
    int m_group_id;
    int m_id;
};

#endif // CPDEFINITION_H
