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
    property var attributes: [
        { width: 20, depth: 20, height: 10, shape: "elliptic" },
        { width: 23, depth: 23, height: 10, shape: "elliptic" },
        { width: 35, depth: 35, height: 10, shape: "elliptic" },
        { width: 60, depth: 60, height: 10, shape: "elliptic" },
        { width: 90, depth: 90, height: 10, shape: "elliptic" }
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