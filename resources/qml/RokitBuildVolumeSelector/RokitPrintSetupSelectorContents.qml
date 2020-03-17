// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 2.3

import UM 1.3 as UM
import Cura 1.0 as Cura

Item
{
    id: content

    property int absoluteMinimumHeight: 200 * screenScaleFactor

    width: UM.Theme.getSize("print_setup_widget").width - 2 * UM.Theme.getSize("default_margin").width
    height: contents.height

    // Catch all mouse events
    MouseArea
    {
        anchors.fill: parent
        hoverEnabled: true
    }

    Item
    {
        id: contents
        // Use the visible property instead of checking the currentModeIndex. That creates a binding that
        // evaluates the new height every time the visible property changes.
        height: rokitPrinterSetup.height

        anchors
        {
            top: parent.top
            left: parent.left
            right: parent.right
        }

        RokitPrinterSetting
        {
            id: rokitPrinterSetup
            anchors
            {
                left: parent.left
                right: parent.right
                top: parent.top
            }
            visible: true
        }
    }
}