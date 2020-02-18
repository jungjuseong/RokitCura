// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 2.3

import UM 1.3 as UM
import Cura 1.0 as Cura

import "PreparingSetting"

Item
{
    id: content

    property int absoluteMinimumHeight: 200 * screenScaleFactor

    width: UM.Theme.getSize("print_setup_widget").width - 2 * UM.Theme.getSize("default_margin").width
    height: contents.height + buttonRow.height

    enum Mode
    {
        Recommended = 0,
        Custom = 1
    }

    // Catch all mouse events
    MouseArea
    {
        anchors.fill: parent
        hoverEnabled: true
    }

    // Set the current mode index to the value that is stored in the preferences or Recommended mode otherwise.
    property int currentModeIndex:
    {
        return PreparingSetupSelectorContents.Mode.Recommended
    }

    Item
    {
        id: contents
        // Use the visible property instead of checking the currentModeIndex. That creates a binding that
        // evaluates the new height every time the visible property changes.
        height: prepareSettings.height

        anchors
        {
            top: parent.top
            left: parent.left
            right: parent.right
        }

        PrepareSettings
        {
            id: prepareSettings
            anchors
            {
                left: parent.left
                right: parent.right
                top: parent.top
            }
            visible: currentModeIndex == PreparintgSetupSelectorContents.Mode.Recommended
        }

    }

    Rectangle
    {
        id: buttonsSeparator

        // The buttonsSeparator is inside the contents. This is to avoid a double line in the bottom
        anchors.bottom: contents.bottom
        width: parent.width
        height: UM.Theme.getSize("default_lining").height
        color: UM.Theme.getColor("lining")
    }

    Item
    {
        id: buttonRow
        property real padding: UM.Theme.getSize("default_margin").width
        height: recommendedButton.height + 2 * padding + (draggableArea.visible ? draggableArea.height : 0)

        anchors
        {
            bottom: parent.bottom
            left: parent.left
            right: parent.right
        }

        //Invisible area at the bottom with which you can resize the panel.
        MouseArea
        {
            id: draggableArea
            anchors
            {
                left: parent.left
                right: parent.right
                bottom: parent.bottom
            }
            height: childrenRect.height
            cursorShape: Qt.SplitVCursor
            visible: currentModeIndex == PreparingSetupSelectorContents.Mode.Custom
            drag
            {
                target: parent
                axis: Drag.YAxis
            }


            Rectangle
            {
                width: parent.width
                height: UM.Theme.getSize("narrow_margin").height
                color: UM.Theme.getColor("secondary")

                Rectangle
                {
                    anchors.bottom: parent.top
                    width: parent.width
                    height: UM.Theme.getSize("default_lining").height
                    color: UM.Theme.getColor("lining")
                }

                UM.RecolorImage
                {
                    width: UM.Theme.getSize("drag_icon").width
                    height: UM.Theme.getSize("drag_icon").height
                    anchors.centerIn: parent

                    source: UM.Theme.getIcon("resize")
                    color: UM.Theme.getColor("small_button_text")
                }
            }
        }
    }
}