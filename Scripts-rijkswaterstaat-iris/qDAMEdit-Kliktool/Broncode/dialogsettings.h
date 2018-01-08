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

#ifndef DIALOGSETTINGS_H
#define DIALOGSETTINGS_H

#include <QDialog>

namespace Ui {
class DialogSettings;
}

class DialogSettings : public QDialog
{
    Q_OBJECT

public:
    explicit DialogSettings(QWidget *parent = 0);
    ~DialogSettings();

    void setGridSpacingX(const double spacing);
    void setGridSpacingY(const double spacing);
    void setWidthTrafficload(const double width);
    void setHelperLineOffset(const double offset);
    double getGridSpacingX() {return m_grid_spacing_x;}
    double getGridSpacingY() {return m_grid_spacing_y;}
    double getWidthTrafficload() {return m_width_trafficload;}
    double getHelperLineOffset() {return m_helper_line_offset;}

private slots:
    void on_dspinboxRasterX_valueChanged(double arg);
    void on_dspinboxRasterY_valueChanged(double arg);
    void on_dspinboxWidthTrafficload_valueChanged(double arg);
    void on_dspinboxOffset_valueChanged(double arg);

private:
    Ui::DialogSettings *ui;

    double m_grid_spacing_x;
    double m_grid_spacing_y;
    double m_width_trafficload;
    double m_helper_line_offset;
};

#endif // DIALOGSETTINGS_H
