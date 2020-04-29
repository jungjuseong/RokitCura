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
    property var well96: { "diameter": 6.5, "depth": 11.0, "centerTocenter": 9.0 }
    property var products: [
        { id: "96", plate: Qt.vector3d(85.4, 127.6, 14.4), wells: well96 },
        { id: "48", plate: Qt.vector3d(85.4, 127.6, 14.4), wells: { "diameter": 9.75, "depth": 11.0, "centerTocenter": 9.0 }},
        { id: "24", plate: Qt.vector3d(85.4, 127.6, 14.4), wells: { "diameter": 15.5, "depth": 11.0, "centerTocenter": 9.0 }},
        { id: "12", plate: Qt.vector3d(85.4, 127.6, 14.4), wells: { "diameter": 21.9, "depth": 11.0, "centerTocenter": 9.0 }},
        { id: "6", plate: Qt.vector3d(85.4, 127.6, 14.4), wells: { "diameter": 35.0, "depth": 11.0, "centerTocenter": 9.0 }}
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