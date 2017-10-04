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

#ifndef QPROJECTVIEW_H
#define QPROJECTVIEW_H

#include <QObject>
#include <QWidget>

#include "project.h"

const int MARGIN = 20;

enum ClickMode {CM_NONE, CM_CPOINT};

class QProjectView : public QWidget
{
    Q_OBJECT
public:
    explicit QProjectView(QWidget *parent = 0);
    ~QProjectView();

    void setProject(Project *project);
    void setCurrentCrosssectionIndex(const int index);
    void setShowGrid(const bool value);
    void setShowHelperLines(const bool value);
    void setShowPoints(const bool value);
    void setGridspacingX(const double grid_spacing) {m_grid_spacing_x = grid_spacing;}
    void setGridspacingY(const double grid_spacing) {m_grid_spacing_y = grid_spacing;}    
    void setHelperLineOffset(const double offset);
    double getHelperLineOffset() {return m_helper_line_offset;}
    double getGridspacingX() {return m_grid_spacing_x;}
    double getGridspacingY() {return m_grid_spacing_y;}
    bool getShowGrid() {return m_show_grid;}
    bool getShowHelperLines() {return m_show_helperlines;}
    bool getShowPoints() {return m_show_points;}

    void setCursorVisible(const bool value);
    void resetView();
    void startClickProces();
    void stopClickProces();

signals:
    void zoomFactorXChanged(int);
    void zoomFactorYChanged(int);
    void selectionProcesEnded();
    void mousePositionChanged(QPointF);
    void lastCPointSelected();
    void updateCharacteristicPointList();
    void newCharacteristicPointAdded(CPoint*);
    void skipCPointTriggered();

public slots:
    void setZoomX(const int zoomfactor);
    void setZoomY(const int zoomfactor);

private:
    Project *m_project;
    double m_helper_line_offset;
    int m_zoomfactor_x;
    int m_zoomfactor_y;
    int m_offset_x;
    int m_offset_y;
    double m_lmin;
    double m_lmax;
    double m_zmin;
    double m_zmax;
    double m_sx;
    double m_sy;
    double m_cmx;
    double m_cmy;
    double m_grid_spacing_x;
    double m_grid_spacing_y;
    bool m_show_grid;
    bool m_show_helperlines;
    bool m_show_points;
    bool m_show_cursor;
    //alvast voorwerk, misschien later kiezen tot wel of niet snappen
    //nu ingesteld op snappen op punten ivm keuze opdrachtgever
    bool m_snap_to_points;
    QPoint m_mouse_pos;
    QPoint m_mouse_down_pos;
    ClickMode m_clickmode;

    // PRIVATE FUNCTIONS
    QPoint worldToScreen(const Point& p);
    QPointF screenToWorld(const QPoint &p);
    void getNextCPoint();
    void drawCrosssection(Crosssection* crs);

    /* EVENTS AND MEMBERS DEALING WITH THE PAINTING */
    void resizeEvent(QResizeEvent *evt);
    void paintEvent(QPaintEvent *evt);

    /* EVENTS AND MEMBERS DEALING WITH THE MOUSE */
    void mouseMoveEvent(QMouseEvent *evt);
    void mousePressEvent(QMouseEvent *evt);
    void mouseReleaseEvent(QMouseEvent *evt);
    void wheelEvent(QWheelEvent *evt);
};

#endif // QPROJECTVIEW_H
