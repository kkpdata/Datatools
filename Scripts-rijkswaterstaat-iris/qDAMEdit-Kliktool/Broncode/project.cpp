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

#include "project.h"
#include "characteristicpoints.h"
#include "constants.h"

#include <QFile>
#include <QTextStream>
#include <QXmlStreamWriter>
#include <QXmlStreamReader>
#include <QMessageBox>

#include <QDebug>

Project::Project()
{
    m_recording = false;
    m_dirty = false;
}

Project::~Project()
{
    clearData();
}

// Delete all data, for example before reading a file.
void Project::clearData()
{
    foreach (Crosssection *crs, m_crosssections) {
        delete crs;
    }
    m_crosssections.clear();
    m_current_cpoint_definition = nullptr;
}

bool Project::getRecording() const
{
    return m_recording;
}

void Project::setRecording(bool value)
{
    m_recording = value;
}

bool Project::isDirty() const
{
    return m_dirty;
}

void Project::setDirty(const bool d)
{
    m_dirty = d;
}

Crosssection *Project::getCurrentCrosssection()
{
    if ((m_current_crosssection_index < 0) || (m_current_crosssection_index >= numCrosssections())) return nullptr;
    return m_crosssections.at(m_current_crosssection_index);
}

int Project::getCurrent_crosssection_index() const
{
    return m_current_crosssection_index;
}

void Project::setCurrent_crosssection_index(int current_crosssection_index)
{
    m_current_crosssection_index = current_crosssection_index;
}

CpDefinition *Project::getCurrentCpDefinition() const
{
    return m_current_cpoint_definition;
}

CpDefinition *Project::getCpDefinitionByID(const int id)
{
    foreach(CpDefinition* def, CharacteristicPoints::getInstance()->getCharacteristicPoints()) {
        if (def->getId() == id) {
            return def;
        }
    }
    return nullptr;
}

void Project::setCurrentCpDefinition(CpDefinition *current_cpoint_definition)
{
    m_current_cpoint_definition = current_cpoint_definition;
}

bool Project::gotoNextCPoint()
{
    m_current_cpoint_definition = nullptr;
    foreach(CpDefinition* def, CharacteristicPoints::getInstance()->getCharacteristicPoints()) {
        if (getCurrentCrosssection() && !getCurrentCrosssection()->getCharacteristicPointById(def->getId())) {
            m_current_cpoint_definition = def;
#ifndef ARABIC_RIGHT_TO_LEFT
            return true;
#endif
        }
    }
    return (m_current_cpoint_definition != nullptr);
}

Crosssection *Project::getCrosssection(const int index)
{
    if(index >= 0 && index < m_crosssections.count())
        return m_crosssections[index];
    return NULL;
}

Crosssection *Project::getCrosssection(const QString label)
{
    foreach (Crosssection* cs, m_crosssections) {
        if (cs->getName() == label) return cs;
    }
    return nullptr;
}

void Project::addCharacteristicPointToCurrentCrosssection(CPoint* point)
{
    Crosssection *crs = getCurrentCrosssection();
    if (crs) {
        crs->addCharacteristicPoint(point);

        if (point->id() == CPoint::RAND_VERKEERSBELASTING_BUITENWAARTS) {
            // Left edge of road, so add right edge as well.
            CPoint *cptl = new CPoint(CPoint::RAND_VERKEERSBELASTING_BINNENWAARTS);
            if (point->skipped()) {
                cptl->setSkipped(true);
            } else {
                cptl->setL(point->l() + m_trafficload_offset);
                cptl->setZ(crs->getZAt(cptl->l()));
            }
            crs->addCharacteristicPoint(cptl);
        } else if (point->id() == CPoint::RAND_VERKEERSBELASTING_BINNENWAARTS) {
            // Right edge of road, so add left edge as well.
            CPoint *cptl = new CPoint(CPoint::RAND_VERKEERSBELASTING_BUITENWAARTS);
            if (point->skipped()) {
                cptl->setSkipped(true);
            } else {
                cptl->setL(point->l() - m_trafficload_offset);
                cptl->setZ(crs->getZAt(cptl->l()));
            }
            crs->addCharacteristicPoint(cptl);
        }
        m_dirty = true;
    }
}

bool Project::readSurface(QTextStream &stream)
{
    clearData();
    CharacteristicPoints::getInstance()->reset();

    while(!stream.atEnd()) {
        QString line = stream.readLine();
        QStringList args = line.split(";");
        if (args.count() < 1) {
            clearData();
            m_readWriteErrorMsg = "Ongeldige of lege regel in surface bestand.";
            return false;
        }

        Point* first_point = nullptr;   // Remember first point in order to calculate the relative distances to this point.
        Crosssection *crs = new Crosssection();
        crs->setName(args[0]);
        for(int i = 1; i < args.count(); i+=3) {

            if ((i+2) >= args.count()) {
                clearData();
                m_readWriteErrorMsg = "Surface bestand bevat minstens één onvolledig punt en kan niet worden ingelezen.";
                return false;
            }

            // Read coordinates.
            bool okx, oky, okz;
            double x = args[i].trimmed().toDouble(&okx);
            double y = args[i+1].trimmed().toDouble(&oky);
            double z = args[i+2].trimmed().toDouble(&okz);

            if (!(okx && oky && okz)) {
                clearData();
                m_readWriteErrorMsg = "Surface bestand bevat minstens één ongeldig coördinaat en kan niet verder worden ingelezen.";
                return false;
            }

            Point* p = new Point(x, y, z, 0);
            if (first_point) {
                p->calculateL(first_point);
            } else {
                first_point = p;
            }
            crs->addSurfacePoint(p);
        }
        m_crosssections.append(crs);
    }
    m_dirty = false;
    return true;
}

bool Project::readAlternativeSurface(QTextStream &stream)
{
    clearData();
    CharacteristicPoints::getInstance()->reset();

    Crosssection* crs = nullptr;
    Point* first_point = nullptr;
    while(!stream.atEnd()) {
        QString line = stream.readLine();
        QStringList args = line.split(";");
        if (args.count() != 6) {
            clearData();
            m_readWriteErrorMsg = "Ongeldige regel in alternatief surface bestand.";
            return false;
        }

        // Check if we are starting a new cross section.
        if (!crs) {
            crs = new Crosssection();
            crs->setName(args[5]);
        } else if (crs->getName() != args[5]) {
            m_crosssections.append(crs);
            crs = new Crosssection();
            crs->setName(args[5]);
            first_point = nullptr;
        }

        // Read coordinates.
        bool okx, oky, okz;
        double x = args[2].trimmed().replace(",", ".").toDouble(&okx);
        double y = args[3].trimmed().replace(",", ".").toDouble(&oky);
        double z = args[4].trimmed().replace(",", ".").toDouble(&okz);

        if (!(okx && oky && okz)) {
            clearData();
            m_readWriteErrorMsg = "Alternatief surface bestand bevat minstens één ongeldig coördinaat en kan niet worden ingelezen.";
            return false;
        }

        Point* p = new Point(x, y, z, 0);
        if (first_point) {
            p->calculateL(first_point);
        } else {
            first_point = p;
        }
        crs->addSurfacePoint(p);
    }
    if (crs) m_crosssections.append(crs);
    m_dirty = false;
    return true;
}

bool Project::readCharacteristicpoints(QTextStream &stream, QString header)
{
    // Delete exiting characteristic points.
    CharacteristicPoints::getInstance()->clear();
    foreach (Crosssection* crs, m_crosssections) {
        foreach(CPoint* cp, crs->getCharacteristicPoints()) {
            delete cp;
        }
    }

    QMap<int, int> idmap;

    QStringList fields = header.split(";");
    int index = 0;
    for(int i = 1; i < fields.count(); i+=3) {
        QString x_field = fields.at(i);
        if ((x_field.size() > 2) && (x_field.left(2) == "X_")) {
            int id = CharacteristicPoints::getInstance()->addCPointDefinition(new CpDefinition(x_field.mid(2), false, 0));
            idmap.insert(index++, id);
        } else {
            m_readWriteErrorMsg = "Characteristic file header is ongeldig.";
            return false;
        }
    }

    while(!stream.atEnd()) {
        QString line = stream.readLine();
        QStringList args = line.split(";");
        if (args.count() < 1) {
            clearData();
            m_readWriteErrorMsg = "Ongeldige of lege regel in characteristic points bestand.";
            return false;
        }

        // Find the right cross section.
        Crosssection *crs = getCrosssection(args[0]);
        if (!crs) {
            m_readWriteErrorMsg = "Characteristic points en Surfaceline bestanden komen niet overeen.";
            return false;
        }

        index = 0;
        for(int i = 1; i < args.count(); i+=3) {

            if ((i+2) >= args.count()) {
                clearData();
                m_readWriteErrorMsg = "Characteristic points bestand bevat minstens één onvolledig punt en kan niet worden ingelezen.";
                return false;
            }

            // Read coordinates.
            bool okx, oky, okz;
            double x = args[i].trimmed().toDouble(&okx);
            double y = args[i+1].trimmed().toDouble(&oky);
            double z = args[i+2].trimmed().toDouble(&okz);

            if (!(okx && oky && okz)) {
                clearData();
                m_readWriteErrorMsg = "Characteristic points bestand bevat minstens één ongeldig coördinaat en kan niet verder worden ingelezen.";
                return false;
            }

            // Point -1,-1,-1 means, not valid.
            int id = idmap.value(index++);
            if ((x > 0) && (crs->getSurfacePoints().count() > 0)) {
                CPoint* cp = new CPoint(id);
                cp->setX(x);
                cp->setY(y);
                cp->setZ(z);
                cp->calculateL(crs->getReferencePoint());
                crs->addCharacteristicPoint(cp);
            }
        }
    }
    m_dirty = false;
    return true;
}

bool Project::readLog(QTextStream &stream)
{
    while(!stream.atEnd()) {
        QString line = stream.readLine();
        QStringList args = line.split(";");
        if (args.count() < 3) {
            clearData();
            m_readWriteErrorMsg = "Ongeldige of lege regel in log bestand.";
            return false;
        }

        // Find the right cross section.
        Crosssection *crs = getCrosssection(args[0]);
        if (!crs) {
            m_readWriteErrorMsg = "Log en Surfaceline bestanden komen niet overeen.";
            return false;
        }

        if (args.at(1) == "TRUE") {
            crs->setDeleted(true);
        } else if (args.at(1) == "FALSE") {
            crs->setDeleted(false);
        } else {
            m_readWriteErrorMsg = "Ongeldig veld in log bestand.";
            return false;
        }

        // Strip leading and trailing quote if neccessary.
        QString comments = args.at(2);
        if ((comments.size() > 2) && (comments.left(1) == "'") && (comments.right(1) == "'")) {
            comments = comments.mid(1, comments.size() - 2);
        }
        crs->getComments()->fromString(comments);
    }
    return true;
}

bool Project::readCsv(QTextStream &stream)
{
    // Read header to determine type of file.
    QString header = stream.readLine();
    if (header == "LOCATIONID;X1;Y1;Z1;.....;Xn;Yn;Zn;(Profiel)") {

        // It's a surfacelines file.
        return readSurface(stream);

    } else if (header == "CODE;SUBCODE;X;Y;Z;LOCATIONID") {

        // It's a surfacelines file type 2.
        return readAlternativeSurface(stream);

    } else if (header.left(13) == "LOCATIONID;X_") {

        // It's a characteristic points file.
        return readCharacteristicpoints(stream, header);

    } else if (header == "profielnaam;Profielverwijderd;Opmerkingen") {

        // It's a log file.
        return readLog(stream);

    } else {
        m_readWriteErrorMsg = "CSV file heeft een onbekende header en kan daarom niet worden geladen.";
        return false;
    }
}

bool Project::readDatabase(QTextStream &stream)
{
    // First clear old data.
    clearData();
    CharacteristicPoints::getInstance()->reset();

    // Then read characteristic points.
    if (stream.readLine() != "*** Knooppunten ***") {
        m_readWriteErrorMsg = "Database bestand bevat geen characteristic points.";
        return false;
    }

    bool ok1, ok2, ok3;
    int nrofProfiles = stream.readLine().toInt(&ok1);
    int nrofColumns = stream.readLine().toInt(&ok2);
    if (!(ok1 && ok2)) {
        m_readWriteErrorMsg = "Ongeldig database bestand.";
        return false;
    }

    for (int i = 0; i < nrofProfiles; i++) {
        if (stream.atEnd()) {
            m_readWriteErrorMsg = "Onvolledig database bestand.";
            return false;
        }
        Crosssection* crs = new Crosssection();
        crs->setName(stream.readLine());
        m_crosssections.append(crs);

        int index = 0;
        for (int j = 0; j < ((nrofColumns - 1) / 3); j ++) {
            double x = stream.readLine().toDouble(&ok1);
            double y = stream.readLine().toDouble(&ok2);
            double z = stream.readLine().toDouble(&ok3);
            if (ok1 && ok2 && ok3) {
                if (index >= CharacteristicPoints::getInstance()->getCharacteristicPoints().count()) {
                    m_readWriteErrorMsg = "Database bestand bevat teveel karakteristieke punten.";
                    return false;
                }
                CpDefinition* def = CharacteristicPoints::getInstance()->getCharacteristicPoints().at(index++);
                if (x >= 0) {
                    CPoint* cp = new CPoint(def->getId());
                    cp->setX(x);
                    cp->setY(y);
                    cp->setZ(z);
                    // Calculate L when the profile has been loaded.
                    crs->addCharacteristicPoint(cp);
                }
            } else {
                m_readWriteErrorMsg = "Ongeldig nummer in database bestand.";
                return false;
            }
        }
    }

    // Then read profiles.
    if (stream.readLine() != "*** Profielen ***") {
        m_readWriteErrorMsg = "Database bestand bevat geen profielen.";
        return false;
    }

    nrofProfiles = stream.readLine().toInt(&ok1);
    nrofColumns = stream.readLine().toInt(&ok2);
    if (!(ok1 && ok2)) {
        m_readWriteErrorMsg = "Ongeldig database bestand.";
        return false;
    }

    for (int i = 0; i < nrofProfiles; i++) {
        if (stream.atEnd()) {
            m_readWriteErrorMsg = "Onvolledig database bestand.";
            return false;
        }
        Crosssection* crs = getCrosssection(stream.readLine());
        if (!crs) {
            m_readWriteErrorMsg = "Inconsistent database bestand.";
            return false;
        }

        Point* first = nullptr;
        for (int j = 0; j < ((nrofColumns - 1) / 3); j ++) {
            double x = stream.readLine().toDouble(&ok1);
            double y = stream.readLine().toDouble(&ok2);
            double z = stream.readLine().toDouble(&ok3);
            if (ok1 && ok2 && ok3) {
                Point* p = new Point(x, y, z, 0);
                if (first) {
                    p->calculateL(first);
                } else {
                    first = p;
                }
                crs->addSurfacePoint(p);
            } else {
                m_readWriteErrorMsg = "Ongeldig nummer in database bestand.";
            }
        }

        // Now we can calculate the L-values of the Characteristic points.
        foreach (CPoint* cp, crs->getCharacteristicPoints()) {
            cp->calculateL(first);
        }
    }

    // Then ignore the point codes.
    if (stream.readLine() != "*** Puntcodes ***") {
        m_readWriteErrorMsg = "Database bestand bevat geen puntcodes.";
        return false;
    }

    nrofProfiles = stream.readLine().toInt(&ok1);
    nrofColumns = stream.readLine().toInt(&ok2);
    if (!(ok1 && ok2)) {
        m_readWriteErrorMsg = "Ongeldig database bestand.";
        return false;
    }

    for (int i = 0; i < nrofProfiles; i++) {
        if (stream.atEnd()) {
            m_readWriteErrorMsg = "Onvolledig database bestand.";
            return false;
        }
        for (int j = 0; j < nrofColumns; j ++) {
            stream.readLine();
        }
    }

    // Finally read the LOG.
    if (stream.readLine() != "*** Process LOG ***") {
        m_readWriteErrorMsg = "Database bestand bevat geen log.";
        return false;
    }

    nrofProfiles = stream.readLine().toInt(&ok1);
    nrofColumns = stream.readLine().toInt(&ok2);
    if (!(ok1 && ok2 && (nrofColumns == 3))) {
        m_readWriteErrorMsg = "Ongeldig database bestand.";
        return false;
    }

    for (int i = 0; i < nrofProfiles; i++) {
        if (stream.atEnd()) {
            m_readWriteErrorMsg = "Onvolledig database bestand.";
            return false;
        }
        Crosssection* crs = getCrosssection(stream.readLine());
        if (!crs) {
            m_readWriteErrorMsg = "Inconsistent database bestand.";
            return false;
        }

        QString deleted = stream.readLine();
        QString comments = stream.readLine();

        if (deleted == "TRUE") {
            crs->setDeleted(true);
        } else if (deleted == "FALSE") {
            crs->setDeleted(false);
        } else {
            m_readWriteErrorMsg = "Ongeldig veld in database bestand.";
            return false;
        }

        // Strip leading and trailing quote if neccessary.
        if ((comments.size() > 2) && (comments.left(1) == "'") && (comments.right(1) == "'")) {
            comments = comments.mid(1, comments.size() - 2);
        }
        crs->getComments()->fromString(comments);
    }

    m_dirty = false;
    return true;
}


bool Project::writeSurfacelines(QTextStream &stream)
{
    stream << "LOCATIONID;X1;Y1;Z1;.....;Xn;Yn;Zn;(Profiel)\r\n";
    foreach (Crosssection *crs, m_crosssections) {
        if (!crs->isDeleted()) {
            stream << crs->getName();
            foreach(Point *p, crs->getSurfacePoints()) {
                stream << ";" << QString::number(p->x(), 'f', 3);
                stream << ";" << QString::number(p->y(), 'f', 3);
                stream << ";" << QString::number(p->z(), 'f', 3);
            }
            stream << "\r\n";
        }
    }
    return true;
}

bool Project::writeCharacteristicpoints(QTextStream &stream)
{
    // First write header.
    stream << "LOCATIONID";
    foreach (CpDefinition* cpd, CharacteristicPoints::getInstance()->getCharacteristicPoints()) {
        stream << ";X_"<< cpd->getName();
        stream << ";Y_"<< cpd->getName();
        stream << ";Z_"<< cpd->getName();
    }
    stream << "\r\n";

    // Then write data.
    foreach (Crosssection * crs, m_crosssections) {
        if (!crs->isDeleted()) {
            stream << crs->getName();
            foreach (CpDefinition* cpd, CharacteristicPoints::getInstance()->getCharacteristicPoints()) {

                // Find value of characteristic point in profile.
                CPoint* cp = crs->getCharacteristicPointById(cpd->getId());
                if (cp && !cp->skipped()) {
                    stream << ";" << QString::number(cp->x(), 'f', 3);
                    stream << ";" << QString::number(cp->y(), 'f', 3);
                    stream << ";" << QString::number(cp->z(), 'f', 3);
                } else {
                    stream << ";-1.000;-1.000;-1.000";
                }
            }
            stream << "\r\n";
        }
    }

    m_dirty = false;
    return true;
}

bool Project::writeLog(QTextStream &stream)
{
    // First write header.
    stream << "profielnaam;Profielverwijderd;Opmerkingen\r\n";

    // Then write data.
    foreach (Crosssection* crs, m_crosssections) {
        stream << crs->getName();
        stream << ";" << (crs->isDeleted() ? "TRUE" : "FALSE");
        stream << ";'" << crs->getComments()->toString() << "'";
        stream << "\r\n";
    }
    return true;
}

bool Project::writeDatabase(QTextStream &stream)
{
    // First write characteristic points.
    stream << "*** Knooppunten ***\r\n";
    stream << QString::number(numCrosssections()) << "\r\n";
    stream << QString::number(CharacteristicPoints::getInstance()->getCharacteristicPoints().size() * 3 + 1) << "\r\n";

    foreach(Crosssection* crs, m_crosssections) {
        stream << crs->getName() << "\r\n";
        foreach (CpDefinition* cpd, CharacteristicPoints::getInstance()->getCharacteristicPoints()) {

            // Find value of characteristic point in profile.
            CPoint* cp = crs->getCharacteristicPointById(cpd->getId());
            if (cp && !cp->skipped()) {
                stream << QString::number(cp->x(), 'f', 3) << "\r\n";
                stream << QString::number(cp->y(), 'f', 3) << "\r\n";
                stream << QString::number(cp->z(), 'f', 3) << "\r\n";
            } else {
                stream << "-1\r\n-1\r\n-1\r\n";
            }
        }
    }

    // Then write profiles.
    stream << "*** Profielen ***\r\n";
    stream << QString::number(numCrosssections()) << "\r\n";
    // Find our maximum number of columns.
    int nrcols = 0;
    foreach (Crosssection* crs, m_crosssections) {
        if (crs->getSurfacePoints().count() > nrcols) nrcols = crs->getSurfacePoints().count();
    }
    stream << QString::number(nrcols * 3 + 1) << "\r\n";
    foreach (Crosssection* crs, m_crosssections) {
        stream << crs->getName() << "\r\n";
        int col = 0;
        foreach (Point* p, crs->getSurfacePoints()) {
            stream << QString::number(p->x(), 'f', 3) << "\r\n";
            stream << QString::number(p->y(), 'f', 3) << "\r\n";
            stream << QString::number(p->z(), 'f', 3) << "\r\n";
            col++;
        }
        for (; col < nrcols; col++) {
            stream << "\r\n\r\n\r\n";
        }
    }

    // Then write point codes.
    stream << "*** Puntcodes ***\r\n";
    stream << QString::number(numCrosssections()) << "\r\n";
    stream << QString::number(nrcols * 2 + 1) << "\r\n";
    foreach (Crosssection* crs, m_crosssections) {
        stream << crs->getName() << "\r\n";
        for (int i = 0; i < nrcols; i++) {
            stream << "99\r\n999\r\n";
        }
    }

    // Then write log part.
    stream << "*** Process LOG ***\r\n";
    stream << QString::number(numCrosssections()) << "\r\n";
    stream << "3\r\n";
    foreach (Crosssection* crs, m_crosssections) {
        stream << crs->getName() << "\r\n";
        stream << (crs->isDeleted() ? "TRUE" : "FALSE") << "\r\n";
        stream << crs->getComments()->toString() << "\r\n";
    }

    m_dirty = false;
    return true;
}

QString Project::getReadWriteErrorMsg()
{
    QString s = m_readWriteErrorMsg;
    m_readWriteErrorMsg.clear();
    return s;
}
