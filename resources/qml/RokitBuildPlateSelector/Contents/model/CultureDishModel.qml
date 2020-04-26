// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 2.3 as Controls2

import UM 1.2 as UM
import Cura 1.0 as Cura

ListModel {
    property string category: "Culture Dish"
    property string shape: "elliptic"

    property var attributes: [
        Qt.vector3d(90,90,10),
        Qt.vector3d(60,60,10),
        Qt.vector3d(35,35,10)
    ]

    ListElement { 
        text: "CD-100090"
    }
    ListElement { 
        text: "CD-100060"
    }
    ListElement { 
        text: "CD-100035"
    }
}