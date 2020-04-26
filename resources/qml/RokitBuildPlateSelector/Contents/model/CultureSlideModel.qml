// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 2.3 as Controls2

import UM 1.2 as UM
import Cura 1.0 as Cura

ListModel {
    property string category: "Culture Slide"
    property string shape: "rectangular"
    property var attributes: [
        Qt.vector3d(25,50,10),
        Qt.vector3d(20,40,10),
        Qt.vector3d(15,30,10)
    ]

    ListElement { 
        text: "3800052CL"
    }
    ListElement { 
        text: "3800056CL"
    }
    ListElement { 
        text: "3800058CL"
    }
}