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
        { width: 90, depth: 90, height: 15, shape: "elliptic" },
        { width: 60, depth: 60, height: 15, shape: "elliptic" },
        { width: 35, depth: 35, height: 15, shape: "elliptic" }
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