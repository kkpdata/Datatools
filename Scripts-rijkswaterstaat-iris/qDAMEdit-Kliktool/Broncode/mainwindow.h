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

#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QLabel>

#include "project.h"

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

    // Override close event to check if changes have been saved.
    void closeEvent (QCloseEvent *event);

private slots:
    void gotoNextCrosssection();
    void updateCharacteristicPointList();
    void newCharacteristicPointAdded(CPoint* cp);
    void on_actionSave_triggered();
    void on_actionOpen_triggered();
    void on_actionQuit_triggered();
    void on_actionStartStop_triggered();
    void on_actionExportImage_triggered();
    void on_mouseLocationChanged(QPointF p);
    void on_actionInfo_triggered();
    void on_actionToStart_triggered();
    void on_actionBackward_triggered();
    void on_actionForward_triggered();
    void on_actionToEnd_triggered();
    void on_profileListWidget_currentRowChanged(int currentRow);
    void on_actionSettings_triggered();
    void on_actionShowLines_toggled(bool arg);
    void on_actionShowGrid_toggled(bool arg);
    void on_actionShowPoints_toggled(bool arg);
    void on_actionReset_zoom_triggered();
    void on_cpointsListWidget_currentRowChanged(int currentRow);
    void on_actionSkip_triggered();
    void on_actionInvalidProfile_triggered(bool checked);
    void on_actionExportAll_triggered();
    void skipCPoint();

    void on_actionReset_triggered();

private:
    Ui::MainWindow *ui;
    Project m_project;
    QLabel *m_lbl_mouse_location;
    QLabel *m_lbl_cross_section;

    void showActiveCrossSection();
    void reloadProfileList();
    void reloadCharacteristicPointList();
    void readSettings();
    void saveSettings();
    void saveComments();
    void skipPoint();
    void fillInFirstAndLastPointAutomatically();
};

#endif // MAINWINDOW_H
