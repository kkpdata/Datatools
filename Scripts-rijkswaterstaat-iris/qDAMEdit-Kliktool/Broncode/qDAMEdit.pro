#-------------------------------------------------
#
# Project created by QtCreator 2016-10-30T13:15:40
#
#-------------------------------------------------

QT       += core gui

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = qDAMEdit
TEMPLATE = app


SOURCES += main.cpp\
        mainwindow.cpp \
    point.cpp \
    crosssection.cpp \
    cpoint.cpp \
    project.cpp \
    qprojectview.cpp \
    dialogsettings.cpp \
    dialogsavefiles.cpp \
    cpdefinition.cpp \
    characteristicpoints.cpp \
    comments.cpp

HEADERS  += mainwindow.h \
    point.h \
    crosssection.h \
    cpoint.h \
    project.h \
    qprojectview.h \
    constants.h \
    dialogsettings.h \
    dialogsavefiles.h \
    cpdefinition.h \
    characteristicpoints.h \
    comments.h

FORMS    += mainwindow.ui \
    dialogsettings.ui \
    dialogsavefiles.ui

RESOURCES += \
    resources.qrc

DISTFILES += \
    qdamedit.rc \
    README \
    LICENCE.txt

RC_FILE = qdamedit.rc

ICON = icons/qdamedit.icns
