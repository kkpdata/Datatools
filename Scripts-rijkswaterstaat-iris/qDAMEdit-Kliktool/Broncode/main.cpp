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

#include "mainwindow.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    // Gloabl settings
    QCoreApplication::setOrganizationName("TwisQ");
    QCoreApplication::setApplicationVersion("1.0.3");
    QCoreApplication::setOrganizationDomain("twisq.nl");
    QCoreApplication::setApplicationName("qDAMEdit");

    QApplication a(argc, argv);
    MainWindow w;
    w.show();
    a.setWindowIcon(QIcon(":/icons/qdamedit.png"));
    return a.exec();
}
