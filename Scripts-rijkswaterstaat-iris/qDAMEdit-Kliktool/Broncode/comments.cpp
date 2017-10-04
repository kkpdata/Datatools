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

#include "comments.h"

// Definitions of standard comments.
QMap<int, QString> Comments::standard_comments;

Comments::Comments()
{
    freeText = "";
    commentsIds.clear();
}

// Load standard comment values.
void Comments::initialize()
{
    standard_comments.insert(1, "Bebouwing in profiel");
    standard_comments.insert(2, "Geen boezem in profiel");
    standard_comments.insert(3, "Geen kade herkenbaar in profiel");
    standard_comments.insert(4, "Geen teensloot");
    standard_comments.insert(5, "Hoog achterland");
    standard_comments.insert(6, "Hoogte<0,5m");
    standard_comments.insert(7, "Voorland is even hoog als kade");
    standard_comments.insert(8, "Vreemd profiel, moet bekeken worden");
}

// Get a list with all standard comment id's.
QList<int> Comments::getAllStandardCommentIds()
{
    return standard_comments.keys();
}

// Look up a standard comment string by its id.
QString Comments::getStandardComment(const int id)
{
    return standard_comments.value(id);
}

// Load comments object from the given string. The string contains comments separated by slashes.
void Comments::fromString(const QString comments_string)
{
    freeText = "";
    commentsIds.clear();
    foreach (QString part, comments_string.split("/")) {
        int id = standard_comments.key(part, 0);
        if (id > 0) {
            commentsIds.append(id);
        } else {
            if (!freeText.isEmpty()) freeText += "/";
            freeText.append(part);
        }
    }
}

// Return all selected standard comments and the freetext as one string. The values are separated by a slash.
QString Comments::toString() const
{
    QString result;
    foreach (int id, commentsIds) {
        if (!result.isEmpty()) result += "/";
        result+=standard_comments.value(id);
    }
    if (!freeText.isEmpty()) {
        if (!result.isEmpty()) result += "/";
        result += freeText;
    }
    return result;
}

// Get the list with selected standard comments.
QList<int> Comments::getCommentsIds() const
{
    return commentsIds;
}

// Set the list of selected standard comments.
// return true if the new list differs from the old list.
bool Comments::setCommentsIds(const QList<int> &value)
{
    // Test if the list is going to change.
    bool dirty = (commentsIds != value);
    commentsIds = value;
    return dirty;
}

// Get the free comment value.
QString Comments::getFreeText() const
{
    return freeText;
}

// Set the free comment value.
// return true if the new text differs from the old text.
bool Comments::setFreeText(const QString &value)
{
    // Test if text has to change.
    bool dirty = (freeText != value);
    freeText = value;
    return dirty;
}
