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
    property var products: [
        { id: "11035", plate: Qt.vector3d(35,35,10) },
        { id: "11060", plate: Qt.vector3d(60,60,10) },
        { id: "11090", plate: Qt.vector3d(90,90,15) },
        { id: "11150", plate: Qt.vector3d(150,150,20) },
        { id: "11151", plate: Qt.vector3d(150,150,25) },
        { id: "20035", plate: Qt.vector3d(35,35,10) },
        { id: "20060", plate: Qt.vector3d(60,60,15) },
        { id: "20100", plate: Qt.vector3d(90,80,20) },
        { id: "20101", plate: Qt.vector3d(90,90,20) },
        { id: "20150", plate: Qt.vector3d(150,150,25) },
        { id: "20151", plate: Qt.vector3d(150,150,20) }
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