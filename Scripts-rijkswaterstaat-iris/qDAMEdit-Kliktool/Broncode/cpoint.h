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

#ifndef CPOINT_H
#define CPOINT_H

#include "point.h"

#include <QString>

// A characteristic point, with ID and position.
class CPoint : public Point
{
public:
    static const int MAAIVELD_BUITENWAARTS = 100;
    static const int TEEN_GEUL = 110;
    static const int INSTEEK_GEUL = 120;
    static const int TEEN_DIJK_BUITENWAARTS = 130;
    static const int KRUIN_BUITENBERM = 140;
    static const int INSTEEK_BUITENBERM = 150;
    static const int KRUIN_BUITENTALUD = 160;
    static const int RAND_VERKEERSBELASTING_BUITENWAARTS = 170;
    static const int RAND_VERKEERSBELASTING_BINNENWAARTS = 180;
    static const int KRUIN_BINNENTALUD = 190;
    static const int INSTEEK_BINNENBERM = 200;
    static const int KRUIN_BINNENBERM = 210;
    static const int TEEN_DIJK_BINNENWAARTS = 220;
    static const int INSTEEK_SLOOT_DIJKZIJDE = 230;
    static const int SLOOTBODEM_DIJKZIJDE = 240;
    static const int SLOOTBODEM_POLDERZIJDE = 250;
    static const int INSTEEK_SLOOT_POLDERZIJDE = 260;
    static const int MAAIVELD_BINNENWAARTS = 270;

    CPoint(const int id);
    CPoint(const int id, Point *p);
    int id() {return m_id;}

    bool skipped() const;
    void setSkipped(bool skipped);

private:
    int m_id;
    bool m_skipped;
};

#endif // CPOINT_H
