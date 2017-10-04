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

#ifndef CROSSSECTION_H
#define CROSSSECTION_H

#include <QList>
#include <QMap>
#include <QString>

#include "point.h"
#include "cpoint.h"
#include "cpdefinition.h"
#include "comments.h"

// A cross section contains all the information of a profile or cross section.
// i.e. surface line points, characteristic points, name and comments.
class Crosssection
{
public:
    Crosssection();
    // The destructor frees all the memory associated to this cross section.
    virtual ~Crosssection();

    QList<Point*> getSurfacePoints() {return m_points;}
    QList<CPoint*> getCharacteristicPoints() {return m_cpoints;}

    int numSurfacePoints() {return m_points.count();}
    int numCharacteristicPoints() {return m_cpoints.count();}

    bool isDeleted() const;
    void setDeleted(bool d);

    void setName(const QString name) {m_name = name;}
    QString getName() {return m_name;}

    Comments* getComments() {return m_comments;}

    void addSurfacePoint(Point *p) {m_points.append(p);}
    void addCharacteristicPoint(CPoint *p);
    void deleteAllCharacteristicPoints();

    double lmin();
    double lmax();
    double zmin();
    double zmax();

    // Get the first point of the cross section. All distances are calculater from here.
    Point *getReferencePoint();
    CPoint *getCharacteristicPointById(const int id);

    // Calculate the height at a specific position of the cross section.
    double getZAt(const double l);

private:
    bool m_deleted;
    QString m_name;
    QList<Point*> m_points;
    QList<CPoint*> m_cpoints;
    Comments* m_comments;
};

#endif // CROSSSECTION_H
