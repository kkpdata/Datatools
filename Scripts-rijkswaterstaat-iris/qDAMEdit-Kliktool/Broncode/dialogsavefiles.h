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

#ifndef DIALOGSAVEFILES_H
#define DIALOGSAVEFILES_H

#include "project.h"
#include <QDialog>

namespace Ui {
class DialogSaveFiles;
}

class DialogSaveFiles : public QDialog
{
    Q_OBJECT

public:
    explicit DialogSaveFiles(QWidget *parent = 0);
    ~DialogSaveFiles();

    void setProject(Project* project);

private slots:
    void on_pushButton_clicked();

    void on_buttonBox_accepted();

private:
    Ui::DialogSaveFiles *ui;

    const QString DEFAULT_FILENAME_SURFACE = "surfacelines.csv";
    const QString DEFAULT_FILENAME_CPOINTS = "characteristicpoints.csv";
    const QString DEFAULT_FILENAME_LOG     = "output_DAM_Edit_log.csv";
    const QString DEFAULT_FILENAME_DB      = "DAM_Edit_Database.ded";

    // Project instance has the data to save.
    Project* m_project;
};

#endif // DIALOGSAVEFILES_H
