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
    id: bioInkRow
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
        text: catalog.i18nc("@label", "Rokit Bio Ink")
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

        Cura.ComboBox
        {

            id: comboBox
            anchors {
                left: fieldLabel.right
                leftMargin: UM.Theme.getSize("default_margin").width
            }
            width: container.controlWidth
            height: container.controlHeight
            model: ListModel {
                id: model
                ListElement { text: "ABS"; color: "Orange" }
                ListElement { text: "CPE"; color: "Orange" }
                ListElement { text: "CPE+"; color: "Orange" }
                ListElement { text: "PC"; color: "Orange" }
                ListElement { text: "PLA"; color: "Orange" }
                ListElement { text: "PP"; color: "Orange" }
                ListElement { text: "TPU 95A"; color: "Orange" }
            }
            textRole: "text"

            currentIndex:
            {
                var currentValue = rokitBioInkType.properties.value
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
                if (rokitBioInkType.properties.value != newValue)
                {
                    if (setValueFunction !== null)
                    {
                        setValueFunction(newValue)
                    }
                    else
                    {
                        rokitBioInkType.setPropertyValue("value", newValue)
                    }
                    forceUpdateOnChangeFunction()
                    afterOnEditingFinishedFunction()
                }
            }
        }

    }

    UM.SettingPropertyProvider
    {
        id: rokitBioInkType
        containerStack: Cura.MachineManager.activeMachine
        removeUnusedValue: false //Doesn't work with settings that are resolved.
        key: "rokit_bio_ink_type"
        watchedProperties: [ "value", "resolve", "enabled" ]
        storeIndex: 0
    }
}


            