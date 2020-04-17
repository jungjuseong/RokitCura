
// Copyright (c) 2019 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.6
import QtQuick.Controls 2.0

import Cura 1.0 as Cura
import UM 1.3 as UM

Rectangle {
    property string name: "Configuration"

    width:  UM.Theme.getSize("rokit_big_item").width
    height: UM.Theme.getSize("rokit_big_item").height
    border.color: UM.Theme.getColor("setting_control_border")
    radius: UM.Theme.getSize("rokit_combobox_radius").height 
    color: UM.Theme.getColor("primary")

    Text {
        anchors{
            verticalCenter: parent.verticalCenter
            left: parent.left
            leftMargin: UM.Theme.getSize("default_margin").width 
        }
        text: name
    }
}