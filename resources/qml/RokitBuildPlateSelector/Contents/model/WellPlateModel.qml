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
    property var external_dimension: Qt.vector3d(85.4, 127.6, 14.4)
    property var products: [
        { id: "96", plate: Qt.vector3d(6.5, 6.5, 10.8) },
        { id: "48", plate: Qt.vector3d(9.75, 9.75, 17.50)},
        { id: "24", plate: Qt.vector3d(15.5, 15.5, 17.50)},
        { id: "12", plate: Qt.vector3d(21.9, 21.9, 17.50)},
        { id: "6", plate: Qt.vector3d(35.0, 35.0, 17.50)}
    ]

    Component.onCompleted: {
        for (var i = 0; i < products.length; i++) {
            const value = products[i].id
            append(createListElement(value));
        }
    }

    function createListElement(value) {
        return {
            text: value
        };
    }
}