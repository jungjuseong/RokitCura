// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 2.3

import UM 1.3 as UM
import Cura 1.0 as Cura

import "Custom"

// 해야할 것
// 1. slice 버튼 기능 추가
// 2. ouput priority 옵션 추가
// 3. build plate 기능 추가
//

Item
{
    id: content

    property int absoluteMinimumHeight: 200 * screenScaleFactor
    property var listHeight: 300  // --

    width: UM.Theme.getSize("print_setup_widget").width - 2 * UM.Theme.getSize("default_margin").width
    height: contents.height + buttonRow.height

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
        height: rokitGenerationSetup.height

        anchors
        {
            top: parent.top
            left: parent.left
            right: parent.right
        }

        // RokitBuildPlateSetting
        RokitGenerationSetup // 핵심 컨텐츠 (이전: customPrintSetup)
        {
            id: rokitGenerationSetup
            anchors
            {
                left: parent.left
                right: parent.right
                top: parent.top
            }
            height: UM.Preferences.getValue("view/generation_settings_list_height") - UM.Theme.getSize("default_margin").height
            Connections
            {
                target: UM.Preferences
                onPreferenceChanged:
                {
                    if (preference !== "view/generation_settings_list_height" && preference !== "general/window_height" && preference !== "general/window_state")
                    {
                        return;
                    }

                    rokitGenerationSetup.height =
                        Math.min
                        (
                            UM.Preferences.getValue("view/generation_settings_list_height"),
                            Math.max
                            (
                                absoluteMinimumHeight,
                                base.height - (rokitGenerationSetup.mapToItem(null, 0, 0).y + buttonRow.height + UM.Theme.getSize("default_margin").height)
                            )
                        );
                }
            }
            visible: true
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
        height: generationButton.height + 2 * padding + (draggableArea.visible ? draggableArea.height : 0)

        anchors
        {
            bottom: parent.bottom
            left: parent.left
            right: parent.right
        }

        Cura.ActionPanelWidget
        {
            id: actionPanelWidget
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.rightMargin: UM.Theme.getSize("thick_margin").width
            anchors.bottomMargin: UM.Theme.getSize("thick_margin").height
        }
    }
}