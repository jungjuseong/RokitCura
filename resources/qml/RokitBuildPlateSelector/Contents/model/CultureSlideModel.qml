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
    property var products: [
        { id: "11035", plate: Qt.vector3d(20,40,12) },
        { id: "11060", plate: Qt.vector3d(30,60,12) },
        { id: "11090", plate: Qt.vector3d(40,80,12) },
    ]

    Component.onCompleted: {
        for (var i = 0; i < products.length; i++) {
            append({text: products[i].id});
        }
    }

    function createListElement(value) {
        return {
            text: value
        };
    }
}