// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 1.1

import UM 1.2 as UM
import Cura 1.0 as Cura


//
//  Rokit Generic Selector
//
Item
{
    id: rokitGenericRow
    height: childrenRect.height

    property real labelColumnWidth: Math.round(width / 2)
    property var curaRecommendedMode: Cura.RecommendedMode {}

    Cura.IconWithText
    {
        id: title
        anchors { 
            top: parent.top
            left: parent.left
        }
        source: UM.Theme.getIcon("circle_outline")
        text: catalog.i18nc("@label", "Rokit Generic")
        font: UM.Theme.getFont("medium")
        width: labelColumnWidth
    }

    Item
    {
        id: container

        property int controlWidth: UM.Theme.getSize("setting_control").width
        property int controlHeight: UM.Theme.getSize("setting_control").height

        height: comboBox.height

        anchors
        {
            top: parent.top

            left: title.right
            right: parent.right
            verticalCenter: title.verticalCenter
        }

        MaterialSelection {
            width: container.controlWidth;
        }

    }

    UM.SettingPropertyProvider
    {
        id: rokitGenericType
        containerStack: Cura.MachineManager.activeMachine
        removeUnusedValue: false //Doesn't work with settings that are resolved.
        key: "rokit_generic_type"
        watchedProperties: [ "value"]
        storeIndex: 0
    }
}


            