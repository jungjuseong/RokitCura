// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 2.3 as Controls2

import UM 1.2 as UM
import Cura 1.0 as Cura

ListModel {
    property string category: "Well Plate"
    property string shape: "elliptic"
    property var attributes: [
        Qt.vector3d(20,20,10),
        Qt.vector3d(23,23,10),
        Qt.vector3d(35,35,10),
        Qt.vector3d(60,60,10),
        Qt.vector3d(90,90,10)
    ]

    ListElement { 
        text: "96"
    }
    ListElement { 
        text: "48"
    }
    ListElement { 
        text: "24"
    }
    ListElement { 
        text: "12"
    }
    ListElement { 
        text: "6"
    }
}