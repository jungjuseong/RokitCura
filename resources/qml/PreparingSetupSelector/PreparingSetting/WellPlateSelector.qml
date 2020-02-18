// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 1.1

import UM 1.2 as UM
import Cura 1.0 as Cura


//
//  Culture Dish Number
//
Item
{
    id: wellPlateRow
    height: childrenRect.height

    property real labelColumnWidth: Math.round(width / 2)
    property var curaRecommendedMode: Cura.RecommendedMode {}

    Cura.IconWithText
    {
        id: wellPlateRowTitle
        anchors { 
            top: parent.top
            left: parent.left
        }
        source: UM.Theme.getIcon("well-plate-6")
        text: catalog.i18nc("@label", "Well plate")
        font: UM.Theme.getFont("medium")
        width: labelColumnWidth
    }

    Item
    {
        id: wellPlateContainer

        property int controlWidth: UM.Theme.getSize("setting_control").width
        property int controlHeight: UM.Theme.getSize("setting_control").height

        height: wellPlateComboBox.height

        anchors
        {
            top: parent.top

            left: wellPlateRowTitle.right
            right: parent.right
            verticalCenter: wellPlateRowTitle.verticalCenter
        }

        Cura.ComboBox
        {

            id: comboBox
            anchors {
                left: fieldLabel.right
                leftMargin: UM.Theme.getSize("default_margin").width
            }
            width: wellPlateContainer.controlWidth
            height: wellPlateContainer.controlHeight
            model: ListModel {
                id: model
                ListElement { text: "96"; color: "Orange" }
                ListElement { text: "48"; color: "Orange" }
                ListElement { text: "24"; color: "Orange" }
                ListElement { text: "12"; color: "Orange" }
                ListElement { text: "6"; color: "Orange" }

            }
            textRole: "text"

            currentIndex:
            {
                var currentValue = wellPlateType.properties.value
                var index = 0
                for (var i = 0; i < model.count; i++)
                {
                    if (model.get(i).value == currentValue)
                    {
                        index = i
                        break
                    }
                }
                return index
            }

            onActivated:
            {
                var newValue = model.get(index).value
                if (wellPlateType.properties.value != newValue)
                {
                    if (setValueFunction !== null)
                    {
                        setValueFunction(newValue)
                    }
                    else
                    {
                        wellPlateType.setPropertyValue("value", newValue)
                    }
                    forceUpdateOnChangeFunction()
                    afterOnEditingFinishedFunction()
                }
            }
        }

    }

    UM.SettingPropertyProvider
    {
        id: wellPlateType
        containerStack: Cura.MachineManager.activeMachine
        removeUnusedValue: false //Doesn't work with settings that are resolved.
        key: "well_plate_type"
        watchedProperties: [ "value", "resolve", "enabled" ]
        storeIndex: 0
    }
}


            