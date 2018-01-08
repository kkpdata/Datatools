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

#include "point.h"
#include <math.h>

Point::Point()
{
    Point(0.0, 0.0, 0.0, 0.0);
}

Point::Point(Point* p)
{
    m_x = p->x();
    m_y = p->y();
    m_z = p->z();
    m_l = p->l();
}

Point::Point(const double x, const double y, const double z, const double l)
{
    m_x = x;
    m_y = y;
    m_z = z;
    m_l = l;
}

void Point::calculateL(Point *base)
{
    //we berekenen de afstand vanaf het eerste ingelezen punt (0.0)
    double dx = m_x - base->x();
    double dy = m_y - base->y();
    m_l = sqrt(dx*dx + dy*dy);
}
