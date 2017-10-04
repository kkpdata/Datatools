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

#include "dialogsettings.h"
#include "ui_dialogsettings.h"

DialogSettings::DialogSettings(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::DialogSettings)
{
    ui->setupUi(this);    
}

DialogSettings::~DialogSettings()
{
    delete ui;
}

void DialogSettings::setGridSpacingX(const double spacing)
{
    m_grid_spacing_x = spacing;
    ui->dspinboxRasterX->setValue(m_grid_spacing_x);
}

void DialogSettings::setGridSpacingY(const double spacing)
{
    m_grid_spacing_y = spacing;
    ui->dspinboxRasterY->setValue(m_grid_spacing_y);
}

void DialogSettings::setWidthTrafficload(const double width)
{
    m_width_trafficload = width;
    ui->dspinboxWidthTrafficload->setValue(m_width_trafficload);
}

void DialogSettings::setHelperLineOffset(const double offset)
{
    m_helper_line_offset = offset;
    ui->dspinboxOffset->setValue(offset);
}

void DialogSettings::on_dspinboxRasterX_valueChanged(double arg)
{
    m_grid_spacing_x = arg;
}

void DialogSettings::on_dspinboxRasterY_valueChanged(double arg)
{
    m_grid_spacing_y = arg;
}

void DialogSettings::on_dspinboxWidthTrafficload_valueChanged(double arg)
{
    m_width_trafficload = arg;
}

void DialogSettings::on_dspinboxOffset_valueChanged(double arg)
{
    m_helper_line_offset = arg;
}
