// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 2.3 as Controls2

import UM 1.2 as UM
import Cura 1.0 as Cura

ListModel {

    property var attributes: [
        { width: 25, depth: 50, height: 10, shape: "rectangular" },
        { width: 20, depth: 40, height: 10, shape: "rectangular" },
        { width: 15, depth: 30, height: 10, shape: "rectangular" }
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