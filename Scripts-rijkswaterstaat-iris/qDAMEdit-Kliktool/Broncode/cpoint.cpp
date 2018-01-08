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

#include "cpoint.h"

CPoint::CPoint(const int id) : Point()
{
    m_id = id;
    m_skipped = false;
}

CPoint::CPoint(const int id, Point *p)
    : Point(p)
{
    m_id = id;
    m_skipped = false;
}

bool CPoint::skipped() const
{
    return m_skipped;
}

void CPoint::setSkipped(bool skipped)
{
    m_skipped = skipped;
}
