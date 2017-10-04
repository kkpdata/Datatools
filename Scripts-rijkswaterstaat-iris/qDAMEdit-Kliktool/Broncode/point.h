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

#ifndef POINT_H
#define POINT_H

// A point with X,Y,Z coordinates. L is the distance to a reference point.
class Point
{
public:
    Point();
    Point(Point* p);
    Point(const double x, const double y, const double z, const double l);

    double x() const {return m_x;}
    double y() const {return m_y;}
    double z() const {return m_z;}
    double l() const {return m_l;}

    void setX(const double x) {m_x = x;}
    void setY(const double y) {m_y = y;}
    void setZ(const double z) {m_z = z;}
    void setL(const double l) {m_l = l;}

    // Calculate the distance to a reference point.
    void calculateL(Point* base);

protected:
    double m_x;
    double m_y;
    double m_z;
    double m_l;
};

#endif // POINT_H
