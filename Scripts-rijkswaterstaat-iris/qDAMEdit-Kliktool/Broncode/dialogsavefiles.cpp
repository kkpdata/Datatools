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

#include "dialogsavefiles.h"
#include "ui_dialogsavefiles.h"

#include <QMessageBox>
#include <QSettings>
#include <QFileDialog>

DialogSaveFiles::DialogSaveFiles(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::DialogSaveFiles)
{
    m_project = nullptr;

    ui->setupUi(this);

    // Retrieve settings form persistent store.
    QSettings settings;
    ui->edit_directory->setText(settings.value("fn_directory", "").toString());
    ui->edit_filename_surfacepoints->setText(settings.value("fn_surfacelines", DEFAULT_FILENAME_SURFACE).toString());
    ui->edit_filename_characteristicpoints->setText(settings.value("fn_characteristicpoints", DEFAULT_FILENAME_CPOINTS).toString());
    ui->edit_filename_log->setText(settings.value("fn_log", DEFAULT_FILENAME_LOG).toString());
    ui->edit_filename_database->setText(settings.value("fn_database", DEFAULT_FILENAME_DB).toString());
    ui->cb_surfacepoints->setChecked(settings.value("cb_surfacelines", true).toBool());
    ui->cb_characteristicpoints->setChecked(settings.value("cb_characteristicpoints", true).toBool());
    ui->cb_log->setChecked(settings.value("cb_log", true).toBool());
    ui->cb_database->setChecked(settings.value("cb_database", true).toBool());
}

DialogSaveFiles::~DialogSaveFiles()
{
    delete ui;
}

void DialogSaveFiles::setProject(Project* project)
{
    m_project = project;
}

void DialogSaveFiles::on_pushButton_clicked()
{
    QString dirname = ui->edit_directory->text();
    dirname = QFileDialog::getExistingDirectory(this, "Kies directory voor bestanden.", dirname);
    if (!dirname.isEmpty()) {
        ui->edit_directory->setText(dirname);
    }
}

void DialogSaveFiles::on_buttonBox_accepted()
{
    // Retrieve values from dialog.
    QString fn_directory = ui->edit_directory->text();
    QString fn_surfacelines = ui->edit_filename_surfacepoints->text();
    QString fn_characteristicpoints = ui->edit_filename_characteristicpoints->text();
    QString fn_log = ui->edit_filename_log->text();
    QString fn_database = ui->edit_filename_database->text();
    bool save_surfacelines = ui->cb_surfacepoints->checkState();
    bool save_characteristicpoints = ui->cb_characteristicpoints->checkState();
    bool save_log = ui->cb_log->checkState();
    bool save_database = ui->cb_database->checkState();


    // Store settings persistently.
    QSettings settings;
    settings.setValue("fn_directory", fn_directory);
    settings.setValue("fn_surfacelines", fn_surfacelines);
    settings.setValue("fn_characteristicpoints", fn_characteristicpoints);
    settings.setValue("fn_log", fn_log);
    settings.setValue("fn_database", fn_database);
    settings.setValue("cb_surfacelines", save_surfacelines);
    settings.setValue("cb_characteristicpoints", save_characteristicpoints);
    settings.setValue("cb_log", save_log);
    settings.setValue("cb_database", save_database);

    // Test if directory exists.
    QDir dir(fn_directory);
    if (!dir.exists()) {
        QMessageBox::warning(this, "Foutmelding", "De gekozen directory bestaat niet. Kies een geldige directory om de bestanden in op te slaan.");
        return;
    }

    // Check if files already exist.
    int nrofWarnings = 0;
    QString existingFiles = "";

    QFileInfo fileinfo_surfacelines(dir, fn_surfacelines);
    if (save_surfacelines) {
        if (fileinfo_surfacelines.exists()) {
            if (nrofWarnings) existingFiles += ", ";
            existingFiles += fn_surfacelines;
            nrofWarnings++;
        }
    }

    QFileInfo fileinfo_characteristicpoints(dir, fn_characteristicpoints);
    if (save_characteristicpoints) {
        if (fileinfo_characteristicpoints.exists()) {
            if (nrofWarnings) existingFiles += ", ";
            existingFiles += fn_characteristicpoints;
            nrofWarnings++;
        }
    }

    QFileInfo fileinfo_log(dir, fn_log);
    if (save_log) {
        if (fileinfo_log.exists()) {
            if (nrofWarnings) existingFiles += ", ";
            existingFiles += fn_log;
            nrofWarnings++;
        }
    }

    QFileInfo fileinfo_database(dir, fn_database);
    if (save_database) {
        if (fileinfo_database.exists()) {
            if (nrofWarnings) existingFiles += ", ";
            existingFiles += fn_database;
            nrofWarnings++;
        }
    }

    if (nrofWarnings) {
        QString message;
        if (nrofWarnings == 1) {
            message = QString("Het bestand %1 bestaat al en zal worden overschreven. Wil je doorgaan?").arg(existingFiles);
        } else {
            message = QString("De bestanden %1 bestaan al en zullen worden overschreven. Wil je doorgaan?").arg(existingFiles);
        }

        if (QMessageBox::question(this, "Bevestiging", message, QMessageBox::Yes|QMessageBox::No) == QMessageBox::StandardButton::No) return;
    }

    // Save data.
    QApplication::setOverrideCursor(Qt::WaitCursor);
    QApplication::processEvents();
    bool ok = true;

    if (save_surfacelines) {
        QFile file_surfacelines(fileinfo_surfacelines.absoluteFilePath());
        if ( file_surfacelines.open(QIODevice::WriteOnly) )
        {
            QTextStream stream( &file_surfacelines );
            ok &= m_project->writeSurfacelines(stream);
            file_surfacelines.close();
        }
    }

    if (save_characteristicpoints) {
        QFile file_characteristicpoints(fileinfo_characteristicpoints.absoluteFilePath());
        if ( file_characteristicpoints.open(QIODevice::WriteOnly) )
        {
            QTextStream stream( &file_characteristicpoints );
            ok &= m_project->writeCharacteristicpoints(stream);
            file_characteristicpoints.close();
        }
    }

    if (save_log) {
        QFile file_log(fileinfo_log.absoluteFilePath());
        if ( file_log.open(QIODevice::WriteOnly) )
        {
            QTextStream stream( &file_log );
            ok &= m_project->writeLog(stream);
            file_log.close();
        }
    }

    if (save_database) {
        QFile file_database(fileinfo_database.absoluteFilePath());
        if ( file_database.open(QIODevice::WriteOnly) )
        {
            QTextStream stream( &file_database );
            ok &= m_project->writeDatabase(stream);
            file_database.close();
        }
    }

    QApplication::restoreOverrideCursor();
}
