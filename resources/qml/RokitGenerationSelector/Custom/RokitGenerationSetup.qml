// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 2.3
import QtQuick.Controls 1.4 as OldControls
import QtQuick.Layouts 1.3

import UM 1.3 as UM
import Cura 1.6 as Cura
import ".."

Item
{
    id: customPrintSetup

    property real padding: UM.Theme.getSize("default_margin").width
    property bool multipleExtruders: extrudersModel.count > 1

    property var extrudersModel: CuraApplication.getExtrudersModel()

    Item
    {
        id: intent
        height: childrenRect.height

        anchors
        {
            top: parent.top
            topMargin: UM.Theme.getSize("default_margin").height
            left: parent.left
            leftMargin: parent.padding
            right: parent.right
            rightMargin: parent.padding
        }

        Label
        {
            id: generationTitleLabel
            anchors
            {
                top: parent.top
                left: parent.left
                right: parent.right
            }
            text: catalog.i18nc("@label", "Generation")
            font: UM.Theme.getFont("large")
            renderType: Text.NativeRendering
            color: UM.Theme.getColor("text")
            verticalAlignment: Text.AlignVCenter
        }

        // NoIntentIcon
        // {
        //     affected_extruders: Cura.MachineManager.extruderPositionsWithNonActiveIntent
        //     intent_type: Cura.MachineManager.activeIntentCategory
        //     anchors.right: intentSelection.left
        //     anchors.rightMargin: UM.Theme.getSize("narrow_margin").width
        //     width: Math.round(generationTitleLabel.height * 0.5)
        //     anchors.verticalCenter: parent.verticalCenter
        //     height: width
        //     visible: affected_extruders.length
        // }
    }

    //Build Plate
    Item{
        id: buildPlateCheck

        height: buildPlateCheckLabel.height + 2* parent.padding

        anchors{
            top: intent.bottom
            topMargin: UM.Theme.getSize("default_margin").height
            left: parent.left
            leftMargin: parent.padding
            right: parent.right
            rightMargin: parent.padding
        }

        Rectangle{
            anchors.fill: parent
            border.width: 1
            border.color: UM.Theme.getColor("lining")
        }

        // Build Plate 부분
        Label
        {
            id: buildPlateCheckLabel
            anchors
            {
                top: parent.top
                bottom: parent.bottom
                left: parent.left
                leftMargin: UM.Theme.getSize("default_margin").width
                //verticalCenter: parent.verticalCenter
            }
            text: catalog.i18nc("@label", "Build Plate")
            font: UM.Theme.getFont("medium")
            renderType: Text.NativeRendering
            color: UM.Theme.getColor("text")
            verticalAlignment: Text.AlignVCenter
        }

        Text
        {
            id: buildPlateCheckValue
            anchors
            {
                top: parent.top
                bottom: parent.bottom
                right: parent.right
                rightMargin: UM.Theme.getSize("default_margin").width
                //verticalCenter: parent.verticalCenter
            }
            text: catalog.i18nc("@label", "Culture Dish : 100090")
            font: UM.Theme.getFont("medium")
            renderType: Text.NativeRendering
            color: UM.Theme.getColor("text")
            verticalAlignment: Text.AlignVCenter
        }
    }

    UM.TabRow
    {
        id: tabBar

        visible: multipleExtruders  // The tab row is only visible when there are more than 1 extruder

        anchors
        {
            top: buildPlateCheck.bottom
            topMargin: UM.Theme.getSize("default_margin").height
            left: parent.left
            leftMargin: parent.padding
            right: parent.right
            rightMargin: parent.padding
        }

        Repeater
        {
            id: repeater
            model: extrudersModel
            delegate: UM.TabRowButton
            {
                contentItem: Item
                {
                    Cura.ExtruderIcon
                    {
                        anchors.horizontalCenter: parent.horizontalCenter
                        materialColor: model.color
                        extruderEnabled: model.enabled
                    }
                }
                onClicked:
                {
                    Cura.ExtruderManager.setActiveExtruderIndex(tabBar.currentIndex)
                }
            }
        }

        //When active extruder changes for some other reason, switch tabs.
        //Don't directly link currentIndex to Cura.ExtruderManager.activeExtruderIndex!
        //This causes a segfault in Qt 5.11. Something with VisualItemModel removing index -1. We have to use setCurrentIndex instead.
        Connections
        {
            target: Cura.ExtruderManager
            onActiveExtruderChanged:
            {
                tabBar.setCurrentIndex(Cura.ExtruderManager.activeExtruderIndex);
            }
        }

        //When the model of the extruders is rebuilt, the list of extruders is briefly emptied and rebuilt.
        //This causes the currentIndex of the tab to be in an invalid position which resets it to 0.
        //Therefore we need to change it back to what it was: The active extruder index.
        Connections
        {
            target: repeater.model
            onModelChanged:
            {
                tabBar.setCurrentIndex(Cura.ExtruderManager.activeExtruderIndex)
            }
        }
    }

    // list 부분 
    Rectangle
    {
        anchors
        {
            top: tabBar.visible ? tabBar.bottom : intent.bottom
            topMargin: -UM.Theme.getSize("default_lining").width
            left: parent.left
            leftMargin: parent.padding
            right: parent.right
            rightMargin: parent.padding
            bottom: parent.bottom
        }
        z: tabBar.z - 1
        // Don't show the border when only one extruder

        border.color: tabBar.visible ? UM.Theme.getColor("lining") : "transparent"
        border.width: UM.Theme.getSize("default_lining").width

        color: UM.Theme.getColor("main_background")

        RokitGenerationList
        {
            anchors // right Margin: narrow  , left Margin: default
            {
                fill: parent
                topMargin: UM.Theme.getSize("default_margin").height
                leftMargin: UM.Theme.getSize("default_margin").width
                // Small space for the scrollbar
                rightMargin: UM.Theme.getSize("narrow_margin").width
                // Compensate for the negative margin in the parent
                bottomMargin: UM.Theme.getSize("default_lining").width
            }

            // Rectangle{
            //     anchors.fill: parent
            //     border.width: 2
            //     border.color: "green"
            // }
        }

        // Cura.RokitGenerationSettingView
        // {
        //     anchors
        //     {
        //         fill: parent
        //         topMargin: UM.Theme.getSize("default_margin").height
        //         leftMargin: UM.Theme.getSize("default_margin").width
        //         // Small space for the scrollbar
        //         rightMargin: UM.Theme.getSize("narrow_margin").width
        //         // Compensate for the negative margin in the parent
        //         bottomMargin: UM.Theme.getSize("default_lining").width
        //     }
        // }
    }
}
