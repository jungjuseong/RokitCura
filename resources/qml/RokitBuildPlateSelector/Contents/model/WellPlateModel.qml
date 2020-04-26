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
    property string shape: "rectangle"
    property var standardWell: "" // { diameter: 6.46, depth: 11.0, centerTocenter: 9.0 }
    property var products: [
        { id: "32296", plate: Qt.vector3d(85.4,127.6,14.4), well: standardWell},
        { id: "32396", plate: Qt.vector3d(85.4,127.6,14.4), well: standardWell},
        { id: "32496", plate: Qt.vector3d(85.4,127.6,14.4), well: standardWell},
        { id: "32596", plate: Qt.vector3d(85.4,127.6,14.4), well: standardWell},
        { id: "32696", plate: Qt.vector3d(85.4,127.6,14.4), well: standardWell},
        { id: "32796", plate: Qt.vector3d(85.4,127.6,14.4), well: standardWell}
    ]

    Component.onCompleted: {
        for (var i = 0; i < products.length; i++) {
            const value = "#" + products[i].id
            append(createListElement(value));
        }
    }

    function createListElement(value) {
        return {
            text: value
        };
    }
}