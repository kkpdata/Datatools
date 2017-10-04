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

#ifndef COMMENTS_H
#define COMMENTS_H

#include <QMap>
#include <QString>
#include <QList>

// The user can put comments to each cross section. He can choose a number of predefined comments.
// And he can also type in the free field. Comments are stored and processed in this class.
class Comments
{
public:
    Comments();

    // Static functions

    // Initialize standard comment values.
    static void initialize();
    // Get a list with all standard comment id's.
    static QList<int> getAllStandardCommentIds();
    // Look up a standard comment string by its id.
    static QString getStandardComment(const int id);

    // Functions for reading and writing.

    // to initialize comments from a single string. String could be read from file for example.
    void fromString(const QString comments_string);
    // to get a string with all comments, For example to save to file.
    QString toString() const;

    // Function to read / write comments.

    // Set the list of selected standard comments.
    // return true if the new list differs from the old list.
    bool setCommentsIds(const QList<int> &value);
    // Get the list with selected standard comments.
    QList<int> getCommentsIds() const;

    // Set the free comment value.
    // return true if the new text differs from the old text.
    bool setFreeText(const QString &value);
    // Get the free comment value.
    QString getFreeText() const;

private:
    // Definition of standard comments.
    static QMap<int, QString> standard_comments;

    // Free text field.
    QString freeText;

    // The selected standard comment values.
    QList<int> commentsIds;
};

#endif // COMMENTS_H
