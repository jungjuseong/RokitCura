// Copyright (c) 2019 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls 2.3 as Controls2
import QtQuick.Controls.Styles 1.4

import UM 1.2 as UM
import Cura 1.6 as Cura
import ".."

Item
{
    id: qualityRow
    height: childrenRect.height

    property real labelColumnWidth: Math.round(width)
    property real settingsColumnWidth: width - labelColumnWidth

    // Here are the elements that are shown in the left column

    Column
    {
        anchors
        {
            left: parent.left
            right: parent.right
        }

        Item
        {
            height: childrenRect.height
            anchors
            {
                left: parent.left
                right: parent.right
            }
            Cura.IconWithText
            {
                id: profileLabel
                source: UM.Theme.getIcon("category_layer_height")
                text: catalog.i18nc("@label", "Culture dish & Well plate")
                font: UM.Theme.getFont("large")
                width: labelColumnWidth
            }
            
        }
    }
}