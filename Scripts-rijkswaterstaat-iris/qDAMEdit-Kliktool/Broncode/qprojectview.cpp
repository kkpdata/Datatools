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

#include "qprojectview.h"
#include "mainwindow.h"
#include "characteristicpoints.h"
#include "math.h"

#include <QPainter>
#include <QMouseEvent>
#include <QStyleOption>
#include <QStyle>

#include "constants.h"

#include <QDebug>


QProjectView::QProjectView(QWidget *parent) : QWidget(parent)
{
    m_project = nullptr;
    m_clickmode = CM_NONE;
    m_zoomfactor_x = DEFAULT_ZOOMFACTOR_X;
    m_zoomfactor_y = DEFAULT_ZOOMFACTOR_Y;
    m_lmin = 0.0;
    m_lmax = 1.0;
    m_zmin = 0.0;
    m_zmax = 1.0;
    m_offset_x = 0;
    m_offset_y = 0;
    m_show_grid = true;
    m_show_cursor = true;
    m_snap_to_points = true; //zie header voor betekenis

    setStyleSheet("background-color:white;");
    setMouseTracking(true);
}

QProjectView::~QProjectView()
{
}

void QProjectView::setProject(Project *project)
{
    m_project = project;
}

void QProjectView::setZoomX(const int zoomfactor)
{
    m_zoomfactor_x = zoomfactor;
    update();
}

void QProjectView::setZoomY(const int zoomfactor)
{
    m_zoomfactor_y = zoomfactor;
    update();
}

void QProjectView::startClickProces()
{
    m_clickmode = CM_CPOINT;
    setStyleSheet("background-color:#99ffcc;");
    getNextCPoint();
    update();
}

void QProjectView::stopClickProces()
{
    m_clickmode = CM_NONE;
    setStyleSheet("background-color:white;");
    update();
    emit(selectionProcesEnded());
}

void QProjectView::getNextCPoint()
{
    if(m_project->gotoNextCPoint()) {
        update();
        // Send signal to mainwindow.
        emit updateCharacteristicPointList();
    } else {
        emit lastCPointSelected();
        if(m_project->getCurrent_crosssection_index() >= (m_project->numCrosssections() - 1))
            stopClickProces();
        else
            getNextCPoint();
    }
}

void QProjectView::setCurrentCrosssectionIndex(const int index)
{
    m_project->setCurrent_crosssection_index(index);
    resetView();
}

void QProjectView::setShowGrid(const bool value)
{
    m_show_grid = value;
    update();
}

void QProjectView::setShowHelperLines(const bool value)
{
    m_show_helperlines = value;
    update();
}

void QProjectView::setShowPoints(const bool value)
{
    m_show_points = value;
    update();
}

void QProjectView::setHelperLineOffset(const double offset)
{
    m_helper_line_offset = offset;
    update();
}

void QProjectView::setCursorVisible(const bool value)
{
    m_show_cursor = value;
    update();
}

void QProjectView::resetView()
{
    Crosssection *crs = m_project->getCurrentCrosssection();
    if(crs!=NULL){
        m_lmin = crs->lmin();
        m_lmax = crs->lmax();
        m_zmin = crs->zmin();
        m_zmax = crs->zmax();

        //calculate scale from given input
        m_sx = (m_lmax - m_lmin) / (width() - 2 * MARGIN);
        m_sy = (m_zmax - m_zmin) / (height() - 2 * MARGIN);

        //calculate the middle of the camera in world coordinats
        m_cmx = m_lmin + (m_lmax - m_lmin) / 2.0;
        m_cmy = m_zmax - (m_zmax - m_zmin) / 2.0;

        m_offset_x = 0;
        m_offset_y = 0;

        update();
    }
}

void QProjectView::resizeEvent(QResizeEvent *evt)
{
    Q_UNUSED(evt);

    if(m_project->getCurrent_crosssection_index() != -1){
        //calculate scale from given input
        m_sx = (m_lmax - m_lmin) / (width() - 2 * MARGIN);
        m_sy = (m_zmax - m_zmin) / (height() - 2 * MARGIN);
        update();
    }
}

void QProjectView::paintEvent(QPaintEvent *evt)
{
    Q_UNUSED(evt);

    //this code is needed for Qt to use a subclasses widget and attach the widget style as specified in the constructor
    QStyleOption opt;
    opt.init(this);
    QPainter painter(this);
    style()->drawPrimitive(QStyle::PE_Widget, &opt, &painter, this);

    //cursor
    if(m_show_cursor)
        painter.drawLine(m_mouse_pos.x(), 0, m_mouse_pos.x(), height());

    Crosssection *crs = m_project->getCurrentCrosssection();

    if(crs)
        drawCrosssection(crs);
}

void QProjectView::drawCrosssection(Crosssection *crs)
{
    QPainter painter(this);
    //bewaar de oude pen
    QPen oldpen = painter.pen();

    if(m_show_grid){
        QPointF topleft = screenToWorld(QPoint(0,0));
        QPointF bottomright = screenToWorld(QPoint(width(),height()));
        Point ptopleft;
        Point pbottomright;

        double xt = topleft.x();
        double yt = topleft.y();

        //de volgende code start het grid vanuit het nulpunt
        double l = copysign(ceil(fabs(xt)/m_grid_spacing_x)*m_grid_spacing_x, xt);
        double z = copysign(ceil(fabs(yt)/m_grid_spacing_y)*m_grid_spacing_y, yt);

        ptopleft.setL(l);
        ptopleft.setZ(z);

        pbottomright.setL(ceil(bottomright.x()));
        pbottomright.setZ(floor(bottomright.y()));

        double x = ptopleft.l();
        while(x<=pbottomright.l()){
            double y = ptopleft.z();
            while(y>=pbottomright.z()){
                Point p(-1, -1, y, x);
                QPoint sp = worldToScreen(p);
                y -= m_grid_spacing_y;
                painter.drawPoint(sp);
            }
            x += m_grid_spacing_x;
        }
    }

    if(m_show_helperlines){
        //de nul lijn
        Point p(0.0, 0.0, 0.0, 0.0);
        QPoint ps1 = worldToScreen(p);

        QPen hlpen(Qt::black);
        hlpen.setStyle(Qt::DashLine);
        painter.setPen(hlpen);
        painter.drawLine(0, ps1.y(), width(), ps1.y());
        painter.drawText(5, ps1.y(), "0.0");

        //de offset lijn
        p.setZ(m_helper_line_offset);
        QPoint ps2 = worldToScreen(p);
        hlpen.setColor(Qt::gray);
        painter.setPen(hlpen);
        painter.drawLine(0, ps2.y(), width(), ps2.y());
        painter.drawText(5, ps2.y(), QString::number(p.z(), 'f', 1));
        painter.setPen(oldpen);
    }

    //een pen voor de punten
    QPen dppen(Qt::blue);
    dppen.setCapStyle(Qt::RoundCap);
    dppen.setWidth(4);

    //DWARSPROFIEL
    Point *p1 = nullptr;
    QPoint ps1;
    foreach (Point* p2, crs->getSurfacePoints()) {
        QPoint ps2 = worldToScreen(*p2);

        if (!p1) {
            p1 = p2;
            if (m_show_points) {
                painter.setPen(dppen);
                painter.drawPoint(ps2);
            }
        } else {
            if (m_show_points) {
                painter.setPen(dppen);
                painter.drawPoint(ps2);
            }
            painter.setPen(oldpen);
            painter.drawLine(ps1, ps2);
        }
        ps1 = ps2;
    }

    //KARAKTERISTIEKE PUNTEN
    QPen kppen(Qt::red);
    kppen.setCapStyle(Qt::RoundCap);
    kppen.setWidth(2);
    painter.setPen(kppen);
    foreach (CPoint *p, crs->getCharacteristicPoints()) {
        if (!p->skipped()) {
            //if close to a char point show the description
            QPoint ps1 = worldToScreen(*p);
            if(abs(m_mouse_pos.x() - ps1.x()) < CPOINT_SNAP_DISTANCE){
                CpDefinition* cpd = m_project->getCpDefinitionByID(p->id());
                if(cpd){
                    //we calculate the text width
                    QFontMetrics fm(painter.font());
                    QString text = QString("%1").arg(cpd->getName());
                    int twidth = fm.width(text);
                    //we check if the text fits on the widget
                    int x = m_mouse_pos.x() + 2;
                    if(m_mouse_pos.x() + twidth > width())
                        x = m_mouse_pos.x() - twidth - 2;
                    painter.drawText(x, m_mouse_pos.y(), text);
                }
            }
            painter.drawEllipse(ps1, 5, 5);
        }
    }
    painter.setPen(oldpen);

    // Show which point to click.
    CpDefinition* cpd = m_project->getCurrentCpDefinition();
    if(cpd && m_clickmode==CM_CPOINT){
        painter.drawText(QPoint(MARGIN, MARGIN - 5), "Selecteer " + cpd->getName());
    }

    if(crs->isDeleted()){
        QPen nopen(Qt::red);
        nopen.setCapStyle(Qt::RoundCap);
        nopen.setWidth(4);
        painter.setPen(nopen);
        painter.drawLine(0,0,width(),height());
        painter.drawLine(0,height(),width(),0);
    }
    painter.setPen(oldpen);
}

void QProjectView::mouseMoveEvent(QMouseEvent *evt)
{
    if(evt->buttons() == Qt::RightButton){
        int dx = evt->x() - m_mouse_pos.x();
        int dy = evt->y() - m_mouse_pos.y();
        m_offset_x += dx;
        m_offset_y += dy;
    }

    if(m_project->getCurrentCrosssection()) {
        emit mousePositionChanged(screenToWorld(evt->pos()));
    }
    m_mouse_pos = evt->pos();
    update();
}

void QProjectView::mousePressEvent(QMouseEvent *evt)
{
    m_mouse_down_pos = evt->pos();
    Crosssection *crs = m_project->getCurrentCrosssection();
    if(crs==NULL) return;    

    if(m_clickmode==CM_CPOINT && evt->button() == Qt::LeftButton){
        QPointF pos = screenToWorld(evt->pos());

        // Check if there is a cpoint to click. It could be there is no point when all cpoints of this cross section have already been clicked.
        if (m_project->getCurrentCpDefinition()) {
            if(m_snap_to_points){
                if(pos.y() > -9999){
                    //loop punten na, check punt waar l dichtste bij pos.x
                    double mindl = 1e9;
                    Point* closest = nullptr;
                    foreach (Point* p, crs->getSurfacePoints()) {
                        double dl = fabs(p->l() - pos.x());
                        if(!closest || (dl < mindl)){
                            mindl = dl;
                            closest = p;
                        }
                    }

                    if(closest){
                        CPoint* cp = new CPoint(m_project->getCurrentCpDefinition()->getId());
                        cp->setL(closest->l());
                        cp->setZ(closest->z());
                        m_project->addCharacteristicPointToCurrentCrosssection(cp);
                        emit newCharacteristicPointAdded(cp);
                        getNextCPoint();
                    }
                }
            } else {
                if(pos.y() > -9999){
                    CPoint* cp = new CPoint(m_project->getCurrentCpDefinition()->getId());
                    cp->setL(pos.x());
                    cp->setZ(pos.y());
                    m_project->addCharacteristicPointToCurrentCrosssection(cp);
                    emit newCharacteristicPointAdded(cp);
                    getNextCPoint();
                }
            }
        }
    }
}

void QProjectView::mouseReleaseEvent(QMouseEvent *evt)
{
    if(evt->pos() == m_mouse_down_pos && m_clickmode==CM_CPOINT && evt->button()==Qt::RightButton)
        emit skipCPointTriggered();
}

void QProjectView::wheelEvent(QWheelEvent *evt)
{
    if(evt->modifiers() & Qt::ShiftModifier){
        m_zoomfactor_x += evt->delta() / 60;
        if(m_zoomfactor_x > MAX_ZOOMFACTOR_X) m_zoomfactor_x = MAX_ZOOMFACTOR_X;
        if(m_zoomfactor_x < MIN_ZOOMFACTOR_X) m_zoomfactor_x = MIN_ZOOMFACTOR_X;
        emit zoomFactorXChanged(m_zoomfactor_x);
        update();
    }else{
        m_zoomfactor_y += evt->delta() / 60;
        if(m_zoomfactor_y > MAX_ZOOMFACTOR_Y) m_zoomfactor_y = MAX_ZOOMFACTOR_Y;
        if(m_zoomfactor_y < MIN_ZOOMFACTOR_Y) m_zoomfactor_y = MIN_ZOOMFACTOR_Y;
        emit zoomFactorYChanged(m_zoomfactor_y);
        update();
    }
}

QPoint QProjectView::worldToScreen(const Point& p)
{
    double dx = p.l() - m_cmx;
    double dy = p.z() - m_cmy;
    int dxpx = int(dx / m_sx * m_zoomfactor_x / 100.0);
    int dypx = int(dy / m_sy * m_zoomfactor_y / 100.0);
    return QPoint(width()/2 + dxpx + m_offset_x, height()/2 - dypx + m_offset_y);
}

QPointF QProjectView::screenToWorld(const QPoint &p)
{
    QPointF result;
    int dx = p.x() - width() / 2 - m_offset_x;
    int dy = p.y() - height() / 2 - m_offset_y;
    double l = m_cmx + dx * m_sx / (m_zoomfactor_x / 100.0);
    double z = m_cmy - dy * m_sy / (m_zoomfactor_y / 100.0);
    result.setX(l);
    result.setY(z);

    Crosssection *crs = m_project->getCurrentCrosssection();
    if(m_clickmode==CM_CPOINT && crs != NULL){
        if(l>=crs->lmin() && l<=crs->lmax()){
            result.setY(crs->getZAt(l));
        }
    }

    return result;
}
