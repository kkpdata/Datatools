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

#include "crosssection.h"
#include "characteristicpoints.h"
#include <math.h>

Crosssection::Crosssection()
{
    m_deleted = false;
    m_comments = new Comments();
}

Crosssection::~Crosssection()
{
    // Delete all surface points.
    foreach(Point* p, m_points) {
        delete p;
    }
    m_points.clear();

    // Delete all characteristic points.
    foreach (CPoint* cp, m_cpoints) {
        delete cp;
    }
    m_cpoints.clear();

    // Delete all comments.
    delete m_comments;
}

bool Crosssection::isDeleted() const
{
    return m_deleted;
}

void Crosssection::setDeleted(bool d)
{
    m_deleted = d;
}

void Crosssection::addCharacteristicPoint(CPoint *point)
{
    // If the surfacepoints are set, calculate x, and y based on point->l.
    if(m_points.count() >= 2) {

        double x0 = m_points[0]->x();
        double y0 = m_points[0]->y();
        double x1 = m_points[m_points.count()-1]->x();
        double y1 = m_points[m_points.count()-1]->y();
        double dx = x1 - x0;
        double dy = y1 - y0;
        double sum = dx*dx + dy*dy;
        double dl = 0.0;
        if(fabs(sum) > 1e-6){
            dl = sqrt(sum);
            point->setX(x0 + (point->l() / dl) * dx);
            point->setY(y0 + (point->l() / dl) * dy);
        }else{
            point->setX(m_points[0]->x());
            point->setY(m_points[0]->y());
        }
    }

    // Check if such a point already exists. If so replace it.
    for (int i = m_cpoints.size() - 1; i >= 0; i--) {
        if (m_cpoints.at(i)->id() == point->id()) {
            delete m_cpoints.at(i);
            m_cpoints.removeAt(i);
        }
    }
    m_cpoints.append(point);
}

// Delete all characteristic points except maaiveld binnenwaarts and maaiveld buitenwaarts.
void Crosssection::deleteAllCharacteristicPoints()
{
    QList<CPoint*> cpoints = m_cpoints;
    m_cpoints.clear();
    foreach (CPoint* cp, cpoints) {
        if ((cp->id() != CPoint::MAAIVELD_BINNENWAARTS) && (cp->id() != CPoint::MAAIVELD_BUITENWAARTS)) {
            delete cp;
        } else {
            m_cpoints.append(cp);
        }
    }
}

double Crosssection::lmin()
{
    double result = 1e9;
    for(int i=0; i<m_points.count(); i++){
        if(m_points.at(i)->l() < result) result = m_points.at(i)->l();
    }
    return result;

}

double Crosssection::lmax()
{
    double result = -1e9;
    for(int i=0; i<m_points.count(); i++){
        if(m_points.at(i)->l() > result) result = m_points.at(i)->l();
    }
    return result;
}

double Crosssection::zmin()
{
    double result = 1e9;
    for(int i=0; i<m_points.count(); i++){
        if(m_points.at(i)->z() < result) result = m_points.at(i)->z();
    }
    return result;
}

double Crosssection::zmax()
{
    double result = -1e9;
    for(int i=0; i<m_points.count(); i++){
        if(m_points.at(i)->z() > result) result = m_points.at(i)->z();
    }
    return result;
}

// Get the first point of the cross section. All distances are calculater from here.
Point *Crosssection::getReferencePoint()
{
    if (m_points.count()) {
        return m_points.at(0);
    }
    return nullptr;
}

CPoint *Crosssection::getCharacteristicPointById(const int id)
{
    for(int i=0; i<m_cpoints.count(); i++){
        if(m_cpoints[i]->id() == id)
            return m_cpoints[i];
    }
    return NULL;
}

// Calculate the height at a specific position of the cross section.
// Use interpolation.
double Crosssection::getZAt(const double l)
{
    if (m_points.count() < 2) return 0.0;
    for(int i=1; i<m_points.count(); i++){
        Point *p1 = m_points[i-1];
        Point *p2 = m_points[i];

        if(p1->l() <= l && l <= p2->l()){
            double l1 = p1->l();
            double l2 = p2->l();
            double z1 = p1->z();
            double z2 = p2->z();

            return z1 + (l - l1) / (l2 - l1) * (z2 - z1);
        }
    }
    return 0.;
}
