// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 1.1
import UM 1.2 as UM

Item {
    id: extruderIconItem

    implicitWidth: UM.Theme.getSize("extruder_icon").width
    implicitHeight: UM.Theme.getSize("extruder_icon").height

    property color materialColor
    property alias textColor: extruderNumberText.color

    UM.RecolorImage {
        id: mainIcon
        anchors.fill: parent
        source: UM.Theme.getIcon((index === 0) ? "extruder_button" : "hk_syringe_button")
        color: materialColor
    }

    Rectangle {
        id: extruderNumberCircle

        width: height
        height: Math.round(parent.height * 0.6)
        radius: (index === 0) ? Math.round(width / 2) : Math.round(width / 3) 
        color: (index === 0) ? materialColor :UM.Theme.getColor("toolbar_background")

        anchors {
            horizontalCenter: parent.horizontalCenter
            top: parent.top
            // The circle needs to be slightly off center (so it sits in the middle of the square bit of the icon)
            topMargin: (parent.height - height) / 2 - 0.1 * parent.height
        }

        Label {
            id: extruderNumberText
            anchors.centerIn: parent
            text: (index === 0) ? "L" : ("R" + index)
            font: UM.Theme.getFont("small")
            color: UM.Theme.getColor("text")
            width: contentWidth
            height: contentHeight
            renderType: Text.NativeRendering
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
    }
}