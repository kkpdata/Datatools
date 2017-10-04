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
#include "ui_mainwindow.h"
#include "constants.h"
#include "characteristicpoints.h"
#include "dialogsettings.h"
#include "dialogsavefiles.h"
#include "comments.h"

#include <QFileDialog>
#include <QDebug>
#include <QDateTime>
#include <QMessageBox>
#include <QSettings>
#include <QCloseEvent>
#include <QProgressDialog>
#include <QDesktopServices>
#include <QTextBrowser>

const double DEFAULT_GRID_SPACING_X = 5.0;
const double DEFAULT_GRID_SPACING_Y = 0.5;
const double DEFAULT_WIDTH_TRAFFICLOAD = 2.5;
const double DEFAULT_HELPER_LINE_OFFSET = 1.0;
const bool DEFAULT_SHOW_GRID = true;
const bool DEFAULT_SHOW_HELPERLINES = true;
const bool DEFAULT_SHOW_POINTS = true;

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    readSettings(); //lees eventuele waarden uit de settings in

    // Add labels to status bar
    m_lbl_mouse_location = new QLabel(this);
    m_lbl_mouse_location->setAlignment(Qt::AlignRight);
    m_lbl_cross_section = new QLabel(this);
    ui->statusBar->addWidget(m_lbl_cross_section);
    ui->statusBar->addPermanentWidget(m_lbl_mouse_location);

    ui->sliderXScale->setMaximum(MAX_ZOOMFACTOR_X);
    ui->sliderYScale->setMaximum(MAX_ZOOMFACTOR_Y);
    ui->sliderXScale->setValue(DEFAULT_ZOOMFACTOR_X);
    ui->sliderYScale->setValue(DEFAULT_ZOOMFACTOR_Y);
    ui->sliderXScale->setMinimum(MIN_ZOOMFACTOR_X);
    ui->sliderYScale->setMinimum(MIN_ZOOMFACTOR_Y);

    //connect the sliders to the projectview and changes from the projectview to the sliders
    connect(ui->sliderXScale, SIGNAL(valueChanged(int)), ui->wProjectView, SLOT(setZoomX(int)));
    connect(ui->sliderYScale, SIGNAL(valueChanged(int)), ui->wProjectView, SLOT(setZoomY(int)));
    connect(ui->wProjectView, SIGNAL(zoomFactorXChanged(int)), ui->sliderXScale, SLOT(setValue(int)));
    connect(ui->wProjectView, SIGNAL(zoomFactorYChanged(int)), ui->sliderYScale, SLOT(setValue(int)));

    //als het laatste punt van een dwarsprofiel geselecteerd wordt gaan we hier naar het volgende dwp
    connect(ui->wProjectView, SIGNAL(lastCPointSelected()), this, SLOT(gotoNextCrosssection()));
    connect(ui->wProjectView, SIGNAL(mousePositionChanged(QPointF)), this, SLOT(on_mouseLocationChanged(QPointF)));
    connect(ui->wProjectView, SIGNAL(updateCharacteristicPointList()), this, SLOT(updateCharacteristicPointList()));
    connect(ui->wProjectView, SIGNAL(newCharacteristicPointAdded(CPoint*)), this, SLOT(newCharacteristicPointAdded(CPoint*)));

    //koppeling maken tussen een rechtsklik op de projectview en het overslaan van een cpoint
    connect(ui->wProjectView, SIGNAL(skipCPointTriggered()), this, SLOT(skipCPoint()));

    ui->wProjectView->setProject(&m_project);

    // Initialize comments view
    Comments::initialize();
    foreach (int comid, Comments::getAllStandardCommentIds()) {
        QString comdes = Comments::getStandardComment(comid);
        QListWidgetItem* item = new QListWidgetItem();
        item->setText(comdes);
        item->setData(Qt::UserRole, comid);
        ui->commentsListWidget->addItem(item);
    }
}

MainWindow::~MainWindow()
{
    saveSettings();
    delete ui;    
}

// ACTIONS

void MainWindow::on_actionSave_triggered()
{
    saveComments();
    DialogSaveFiles *dlg = new DialogSaveFiles(this);
    dlg->setProject(&m_project);
    dlg->exec();
}

void MainWindow::on_actionOpen_triggered()
{
    if (m_project.isDirty()) {
        if (QMessageBox::question(this, "Bevestiging", "Het project bevat nog niet opgeslagen wijzigingen. Weet je zeker dat je een nieuw bestand wilt openen?", QMessageBox::Yes|QMessageBox::No) ==
                QMessageBox::StandardButton::No) return;
    }

    // Make sure we are not recording.
    m_project.setRecording(false);
    ui->wProjectView->stopClickProces();
    ui->menuBewerken->actions()[0]->setChecked(false);

    QSettings settings;
    QString dir = settings.value("open_dir").toString();
    QString filename = QFileDialog::getOpenFileName(this, tr("Bestand openen..."), dir, tr("qDAMEdit bestanden (*.csv *.ded)"));
    if(filename!=""){
        ui->profileListWidget->clear();
        QFile file(filename);
        QFileInfo fileinfo(file);
        settings.setValue("open_dir", fileinfo.absolutePath());
        if (!file.open(QIODevice::ReadOnly)){
            QMessageBox::critical(NULL, "Foutmelding", "Het bestand " + filename + " is niet leesbaar.");
            return;
        }
        QTextStream in(&file);
        bool ok;
        if (filename.right(3).toLower() == "ded") {
            ok = m_project.readDatabase(in);
        } else {
            ok = m_project.readCsv(in);
        }
        if (!ok) {
            QMessageBox::warning(this, "Foutmelding", m_project.getReadWriteErrorMsg());
        }
        m_project.setCurrent_crosssection_index(0);
        reloadProfileList();
        reloadCharacteristicPointList();
        showActiveCrossSection();
        ui->logTextEdit->clear();
        file.close();
    }
}

void MainWindow::on_actionQuit_triggered()
{
    close();
}

void MainWindow::on_actionStartStop_triggered()
{
    if(m_project.getRecording()) {
        m_project.setRecording(false);
        ui->wProjectView->stopClickProces();
    } else {
        if (m_project.getCurrentCrosssection()) {
            m_project.setRecording(true);
            showActiveCrossSection();
            ui->wProjectView->startClickProces();
        }
    }
}

void MainWindow::on_actionExportImage_triggered()
{
    Crosssection* crs = m_project.getCurrentCrosssection();

    if(crs){
        QSettings settings;
        QString startdir = settings.value("images_directory", "").toString();
        QString filename = QString("%1.png").arg(crs->getName());
        QFileInfo preferredfile(QDir(startdir), filename);
        filename = QFileDialog::getSaveFileName(this, "Kies bestandsnaam voor afbeelding.", preferredfile.absoluteFilePath(), "*.png");
        if (!filename.isEmpty()) {
            QFileInfo fileinfo(filename);
            settings.setValue("images_directory", fileinfo.absolutePath());

            //maak de cursor even onzichtbaar en doe de export
            ui->wProjectView->setCursorVisible(false);
            ui->wProjectView->grab().save(filename);
            //en weer zichtbaar
            ui->wProjectView->setCursorVisible(true);
            QMessageBox::information( this, "Image save", QString("De afbeelding is opgeslagen als %1").arg(filename), QMessageBox::Ok, 0 );
        }
    }
}

void MainWindow::on_actionInfo_triggered()
{
    QString version = QCoreApplication::applicationVersion();
    QString html = "<html><body><h1>qDAMEdit</h1><p>Deze software kan worden gebruikt voor het aangeven van de karakteristieke punten in dijkprofielen.</p>";
    html += "<p><table>";
    html += "<tr><td>Versie:</td><td>" + version + "</td></tr>";
    html += "<tr><td>Copyright:</td><td>TWISQ</td></tr>";
    html += "<tr><td>Opdrachtgever:</td><td>Rijkswaterstaat</td></tr>";
    html += "<tr><td>Iconen:</td><td><a href='http://www.famfamfam.com/lab/icons/silk/'>Fam Fam Fam</a></td></tr>";
    html += "<tr><td>Help:</td><td><a href='http://www.twisq.nl/qdamedit/manual.pdf'>http://www.twisq.nl/qdamedit/manual.pdf</a></td></tr>";
    html += "</table></p>";
    html += "<p>Deze software is open source en uitgebracht onder de GNU GPLv3 licentie. Dat betekent dat je vrij bent om de software te gebruiken, copieren, aanpassen en distribueren, mits je de oorspronkelijke auteur vermeldt en geen aanvullende restricties oplegt. Een volledige beschrijving van GNU GPLv3 kan je <a href='https://www.gnu.org/licenses/gpl.html'>hier</a> lezen.</p>";
    html += "<p>qDAMEdit is geschreven in Qt versie 5.9.</p>";
    html += "</body></html>";
    QMessageBox::about(this, "qDAMEdit", html);
}

void MainWindow::on_actionToStart_triggered()
{
    if (m_project.numCrosssections() > 0) {
        saveComments();
        m_project.setCurrent_crosssection_index(0);
        showActiveCrossSection();
    }
}

void MainWindow::on_actionBackward_triggered()
{
    if (m_project.getCurrent_crosssection_index() > 0) {
        m_project.setCurrent_crosssection_index(m_project.getCurrent_crosssection_index() - 1);
        showActiveCrossSection();
    }
}

void MainWindow::on_actionForward_triggered()
{
    gotoNextCrosssection();
}

void MainWindow::on_actionToEnd_triggered()
{
    if (m_project.numCrosssections() > 0) {
        saveComments();
        m_project.setCurrent_crosssection_index(m_project.numCrosssections() - 1);
        showActiveCrossSection();
    }
}

void MainWindow::on_actionSettings_triggered()
{
    DialogSettings *dlg = new DialogSettings(this);
    dlg->setGridSpacingX(ui->wProjectView->getGridspacingX());
    dlg->setGridSpacingY(ui->wProjectView->getGridspacingY());
    dlg->setWidthTrafficload(m_project.getTrafficloadOffset());
    dlg->setHelperLineOffset(ui->wProjectView->getHelperLineOffset());

    if(dlg->exec()){
        ui->wProjectView->setGridspacingX(dlg->getGridSpacingX());
        ui->wProjectView->setGridspacingY(dlg->getGridSpacingY());
        ui->wProjectView->setHelperLineOffset(dlg->getHelperLineOffset());

        //TODO als de traffic breedte verandert moeten alle profielen aangepast worden op de nieuwe waarde!
        //Dit kan leiden tot ongeldige punten
        m_project.setTrafficloadOffset(dlg->getWidthTrafficload());
        ui->wProjectView->repaint();
    }

}

void MainWindow::on_actionShowLines_toggled(bool arg)
{
    ui->wProjectView->setShowHelperLines(arg);
}

void MainWindow::on_actionShowGrid_toggled(bool arg)
{
    ui->wProjectView->setShowGrid(arg);
}

void MainWindow::on_actionShowPoints_toggled(bool arg)
{
    ui->wProjectView->setShowPoints(arg);
}

void MainWindow::on_actionReset_zoom_triggered()
{
    ui->sliderXScale->setValue(DEFAULT_ZOOMFACTOR_X);
    ui->sliderYScale->setValue(DEFAULT_ZOOMFACTOR_Y);
    ui->wProjectView->resetView();
}

void MainWindow::on_cpointsListWidget_currentRowChanged(int currentRow)
{
    CpDefinition* def = (CpDefinition*) ui->cpointsListWidget->item(currentRow)->data(Qt::UserRole).toLongLong();
    if (def) {
        m_project.setCurrentCpDefinition(def);
        ui->wProjectView->update();
    }
}

void MainWindow::on_actionSkip_triggered()
{
    skipPoint();
}


void MainWindow::on_actionInvalidProfile_triggered(bool checked)
{
    Crosssection *crs = m_project.getCrosssection(m_project.getCurrent_crosssection_index());
    if(crs){
        crs->setDeleted(checked);
        ui->wProjectView->update();
        if(checked){
            ui->profileListWidget->item(m_project.getCurrent_crosssection_index())->setForeground(Qt::red);
        }else{
            ui->profileListWidget->item(m_project.getCurrent_crosssection_index())->setForeground(Qt::black);
        }
    }
}

void MainWindow::on_actionExportAll_triggered()
{
    //is er uberhaupt iets te doen?
        if(m_project.numCrosssections()==0) return;

        //bewaar de huidige selectie
        int ccrsid = m_project.getCurrent_crosssection_index();
        //selecteer het uitvoerpad
        QSettings settings;
        QString startdir = settings.value("images_directory", "").toString();

        QString exportdir = QFileDialog::getExistingDirectory(this, tr("Selecteer uitvoerpad"),
                                                     startdir,
                                                     QFileDialog::ShowDirsOnly
                                                     | QFileDialog::DontResolveSymlinks);

        //cancel opvangen
        if(exportdir.length()==0) return;

        // Store path
        settings.setValue("images_directory", exportdir);

        QCoreApplication::processEvents(); //soms werkt dit om te voorkomen dat de dialoog niet verschijnt

        //maak een nieuwe projectview en gebruik dezelfde functionaliteit van een enkele screenshot
        QProjectView *view = new QProjectView();
        view->resize(800,600);
        view->setShowGrid(false);
        view->setShowHelperLines(true);
        view->setShowPoints(true);
        view->setProject(&m_project);
        view->setCursorVisible(false);

        QProgressDialog dlg("Bezig met het exporteren van de dwarsprofiel afbeeldingen", "Onderbreken", 0, m_project.numCrosssections(), this);
        dlg.setWindowModality(Qt::WindowModal);

        for (int i=0; i<m_project.numCrosssections()-1; i++) {
            dlg.setValue(i);
            if(dlg.wasCanceled()) break;
            Crosssection *crs = m_project.getCrosssection(i);
            QString filename = QString("%1.png").arg(crs->getName());
            QFileInfo fileinfo(QDir(exportdir), filename);
            view->setCurrentCrosssectionIndex(i);
            view->grab().save(fileinfo.absoluteFilePath());
        }
        dlg.setValue(m_project.numCrosssections());
        delete view;

        //reset het actuele dwarsprofiel
        m_project.setCurrent_crosssection_index(ccrsid);

        QMessageBox::information(this, "Afbeeldingen export", QString("De afbeeldingen zijn opgeslagen in %1").arg(exportdir), QMessageBox::Ok, 0 );
}

void MainWindow::skipCPoint()
{
    skipPoint();
}

void MainWindow::on_mouseLocationChanged(QPointF p)
{
    if(m_project.numCrosssections()>0) {
        m_lbl_mouse_location->setText(QString("X = %1, Y = %2").arg(p.x(), 5, 'f', 2).arg(p.y(), 5, 'f', 2));
    }
}

void MainWindow::on_profileListWidget_currentRowChanged(int currentRow)
{
    if ((currentRow >= 0) && (currentRow < m_project.numCrosssections())) {
        saveComments();
        m_project.setCurrent_crosssection_index(currentRow);
        showActiveCrossSection();
    }
}

void MainWindow::closeEvent (QCloseEvent *event)
{
    if (m_project.isDirty()) {
        if (QMessageBox::question(this, "Bevestiging", "Het project bevat nog niet opgeslagen wijzigingen. Weet je zeker dat je wilt afsluiten?", QMessageBox::Yes|QMessageBox::No) ==
                QMessageBox::StandardButton::No) {
            event->ignore();
        }
    }
}

void MainWindow::reloadProfileList()
{
    int n = m_project.numCrosssections();
    Crosssection* p;
    for (int i = 0; i < n; i++) {
        p = m_project.getCrosssection(i);
        if (p){
            ui->profileListWidget->addItem(p->getName());
            if(p->isDeleted()){
                ui->profileListWidget->item(i)->setForeground(Qt::red);
            }else{
                ui->profileListWidget->item(i)->setForeground(Qt::black);
            }

        }
    }
    if (ui->profileListWidget->count() > 0) {
        ui->profileListWidget->item(0)->setSelected(true);
        ui->profileListWidget->setCurrentRow(0);
    }
}

void MainWindow::reloadCharacteristicPointList()
{
    ui->cpointsListWidget->clear();
    int i = 0;
    foreach(CpDefinition* def, CharacteristicPoints::getInstance()->getCharacteristicPoints()) {
#ifdef ARABIC_RIGHT_TO_LEFT
        ui->cpointsListWidget->insertItem(0, def->getName());
        ui->cpointsListWidget->item(0)->setData(Qt::UserRole, ((qlonglong)def));
#else
        ui->cpointsListWidget->addItem(def->getName());
        ui->cpointsListWidget->item(i)->setData(Qt::UserRole, ((qlonglong)def));
#endif
        i++;
    }
    updateCharacteristicPointList();
}

void MainWindow::updateCharacteristicPointList()
{
    Crosssection* crs = m_project.getCurrentCrosssection();
    if (crs) {
        for (int i = 0; i < ui->cpointsListWidget->count(); i++) {
            CpDefinition* def = (CpDefinition*) ui->cpointsListWidget->item(i)->data(Qt::UserRole).toLongLong();
            CPoint* cp = crs->getCharacteristicPointById(def->getId());
            if (cp) {
                if (cp->skipped()) {
                    ui->cpointsListWidget->item(i)->setForeground(Qt::red);
                } else {
                    ui->cpointsListWidget->item(i)->setForeground(Qt::darkGreen);
                }
            } else {
                ui->cpointsListWidget->item(i)->setForeground(Qt::gray);
            }
            if (m_project.getRecording()) {
                if (m_project.getCurrentCpDefinition() && (m_project.getCurrentCpDefinition()->getId() == def->getId())) {
                    ui->cpointsListWidget->item(i)->setSelected(true);
                    ui->cpointsListWidget->scrollToItem(ui->cpointsListWidget->item(i));
                }
            } else {
                ui->cpointsListWidget->item(i)->setSelected(false);
            }
        }
    }
}

void MainWindow::newCharacteristicPointAdded(CPoint *cp)
{
    CpDefinition* cpd = CharacteristicPoints::getInstance()->lookupCPointDefinition(cp->id());
    if (cpd) {
        QString s = cpd->getName() + "\n";
        QTextCursor cursor = ui->logTextEdit->textCursor();
        cursor.movePosition(QTextCursor::End);
        cursor.insertText(s);
        s = QString("X = %1 Y = %2 Z = %3\n").arg(cp->x(), 5, 'f', 2).arg(cp->y(), 5, 'f', 2).arg(cp->z(), 5, 'f', 2);
        cursor.insertText(s);
        ui->logTextEdit->setTextCursor(cursor);
        ui->logTextEdit->ensureCursorVisible();
    }
}

void MainWindow::showActiveCrossSection()
{
    QString s;
    if (m_project.numCrosssections() > 0) {
        fillInFirstAndLastPointAutomatically();

        ui->profileListWidget->item(m_project.getCurrent_crosssection_index())->setSelected(true);
        ui->profileListWidget->setCurrentRow(m_project.getCurrent_crosssection_index());
        ui->profileListWidget->scrollToItem(ui->profileListWidget->item(m_project.getCurrent_crosssection_index()));
        ui->wProjectView->setCurrentCrosssectionIndex(m_project.getCurrent_crosssection_index());        

        // Update status bar.
        s = QString("Profiel: %1 / %2").arg(m_project.getCurrent_crosssection_index() + 1).arg(m_project.numCrosssections());

        // Show comments.
        QList<int> selectedIds = m_project.getCurrentCrosssection()->getComments()->getCommentsIds();
        for (int i = 0; i < ui->commentsListWidget->count(); i++) {
            int thisId = ui->commentsListWidget->item(i)->data(Qt::UserRole).toInt();
            ui->commentsListWidget->item(i)->setSelected(selectedIds.contains(thisId));
        }
        ui->commentsTextEdit->setText(m_project.getCurrentCrosssection()->getComments()->getFreeText());

        //update status of skip button in toolbar
        ui->actionInvalidProfile->setChecked(m_project.getCurrentCrosssection()->isDeleted());
    } else {
        s = "Geen profielen geladen";
    }
    m_lbl_cross_section->setText(s);
    m_project.gotoNextCPoint();
    updateCharacteristicPointList();
}

// The crosssection is probably about to change. Save comments in current cross section.
void MainWindow::saveComments()
{
    if (m_project.getCurrentCrosssection() && m_project.getRecording()) {

        // First save the free text.
        if (m_project.getCurrentCrosssection()->getComments()->setFreeText(ui->commentsTextEdit->toPlainText())) {
            m_project.setDirty(true);
        }

        // Then save the standard comment messages.
        QList<int> selectedIds;
        foreach (QListWidgetItem* item, ui->commentsListWidget->selectedItems()) {
            selectedIds.append(item->data(Qt::UserRole).toInt());
        }
        if (m_project.getCurrentCrosssection()->getComments()->setCommentsIds(selectedIds)) {
            m_project.setDirty(true);
        }
    }
}

// Skip current characteristic point and all points from the same group.
void MainWindow::skipPoint()
{
    if (m_project.getCurrentCpDefinition() && m_project.getCurrentCrosssection()) {
        // Get group id.
        int groupid = m_project.getCurrentCpDefinition()->getGroupId();

        // Find all characteristic points with the same group id.
        foreach(CpDefinition* def, CharacteristicPoints::getInstance()->getCharacteristicPoints()) {
            if (def->getGroupId() == groupid) {
                if (!m_project.getCurrentCrosssection()->getCharacteristicPointById(def->getId())) {
                    CPoint* cp = new CPoint(def->getId());
                    cp->setSkipped(true);
                    m_project.addCharacteristicPointToCurrentCrosssection(cp);
                } else {
                    m_project.getCurrentCrosssection()->getCharacteristicPointById(def->getId())->setSkipped(true);
                }
            }
        }
        if (!m_project.gotoNextCPoint())
            gotoNextCrosssection();

        ui->wProjectView->update();
        updateCharacteristicPointList();
    }
}

void MainWindow::readSettings()
{
    // Organization and application name are given in main.cpp
    QSettings settings;
    ui->wProjectView->setGridspacingX(settings.value("gridSpacingX", DEFAULT_GRID_SPACING_X).toDouble());
    ui->wProjectView->setGridspacingY(settings.value("gridSpacingY", DEFAULT_GRID_SPACING_Y).toDouble());
    //m_width_trafficload = settings.value("widthTrafficLoad", DEFAULT_WIDTH_TRAFFICLOAD).toDouble();
    m_project.setTrafficloadOffset(settings.value("widthTrafficLoad", DEFAULT_WIDTH_TRAFFICLOAD).toDouble());
    ui->wProjectView->setHelperLineOffset(settings.value("helperLineOffset", DEFAULT_HELPER_LINE_OFFSET).toDouble());
    ui->wProjectView->setShowGrid(settings.value("showGrid", DEFAULT_SHOW_GRID).toBool());
    ui->actionShowGrid->setChecked(ui->wProjectView->getShowGrid());
    ui->wProjectView->setShowHelperLines(settings.value("showHelperLines", DEFAULT_SHOW_HELPERLINES).toBool());
    ui->actionShowLines->setChecked(ui->wProjectView->getShowHelperLines());
    ui->wProjectView->setShowPoints(settings.value("showPoints", DEFAULT_SHOW_POINTS).toBool());
    ui->actionShowPoints->setChecked(ui->wProjectView->getShowPoints());

}

void MainWindow::saveSettings()
{
    // Organization and application name are given in main.cpp
    QSettings settings;
    settings.setValue("gridSpacingX", ui->wProjectView->getGridspacingX());
    settings.setValue("gridSpacingY", ui->wProjectView->getGridspacingY());
    settings.setValue("widthTrafficLoad", m_project.getTrafficloadOffset());
    settings.setValue("helperLineOffset", ui->wProjectView->getHelperLineOffset());
    settings.setValue("showGrid", ui->wProjectView->getShowGrid());
    settings.setValue("showHelperLines", ui->wProjectView->getShowHelperLines());
    settings.setValue("showPoints", ui->wProjectView->getShowPoints());
}

void MainWindow::gotoNextCrosssection()
{
    saveComments();
    if (m_project.getCurrent_crosssection_index() < (m_project.numCrosssections() - 1)) {        
        m_project.setCurrent_crosssection_index(m_project.getCurrent_crosssection_index() + 1);
        showActiveCrossSection();
    } else {
        m_project.setRecording(false);
        ui->wProjectView->stopClickProces();
    }
}

// The first and last characteristic points can be filled in automatcally.
// These are the first and last ones of the surfacelines.
void MainWindow::fillInFirstAndLastPointAutomatically()
{
    Crosssection* crs = m_project.getCurrentCrosssection();
    if (m_project.getRecording() && crs) {

        // Add Maaiveld Binnenwaards if it is not already there.
        if (!crs->getCharacteristicPointById(CPoint::MAAIVELD_BINNENWAARTS)) {
            Point *p = crs->getSurfacePoints().last();
            CPoint* cp = new CPoint(CPoint::MAAIVELD_BINNENWAARTS, p);
            crs->addCharacteristicPoint(cp);
        }

        // Add Maaiveld Buitenwaards if it is not already there.
        if (!crs->getCharacteristicPointById(CPoint::MAAIVELD_BUITENWAARTS)) {
            Point *p = crs->getSurfacePoints().first();
            CPoint* cp = new CPoint(CPoint::MAAIVELD_BUITENWAARTS, p);
            crs->addCharacteristicPoint(cp);
        }
    }
}

// Delete all characteristic points except for the maaiveld binnenwaarts and maaiveld buitenwaarts.
void MainWindow::on_actionReset_triggered()
{
    Crosssection* crs = m_project.getCurrentCrosssection();
    if (crs && m_project.getRecording()) {
        crs->deleteAllCharacteristicPoints();
        showActiveCrossSection();
    }
}
