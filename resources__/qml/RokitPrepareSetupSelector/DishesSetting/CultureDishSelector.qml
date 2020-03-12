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
    id: cultureDishRow
    height: childrenRect.height

    property real labelColumnWidth: Math.round(width / 2)
    property var curaRecommendedMode: Cura.RecommendedMode {}

    Cura.IconWithText
    {
        id: cultureDishRowTitle
        anchors { 
            top: parent.top
            left: parent.left
        }
        source: UM.Theme.getIcon("circle_outline")
        text: catalog.i18nc("@label", "Culture dish #")
        font: UM.Theme.getFont("medium")
        width: labelColumnWidth
    }

    Item
    {
        id: cultureDishContainer

        property int controlWidth: UM.Theme.getSize("setting_control").width
        property int controlHeight: UM.Theme.getSize("setting_control").height

        height: cultureDishComboBox.height

        anchors
        {
            top: parent.top

            left: cultureDishRowTitle.right
            right: parent.right
            verticalCenter: cultureDishRowTitle.verticalCenter
        }

        Cura.ComboBox
        {

            id: cultureDishComboBox
            anchors {
                left: fieldLabel.right
                leftMargin: UM.Theme.getSize("default_margin").width
            }
            width: cultureDishContainer.controlWidth
            height: cultureDishContainer.controlHeight
            model: ListModel {
                id: model
                ListElement { text: "3800052CL"; color: "Orange" }
                ListElement { text: "3800056CL"; color: "Orange" }
                ListElement { text: "3800058CL"; color: "Orange" }
            }
            textRole: "text"

            currentIndex:
            {
                var currentValue = propertyProvider.properties.value
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
                if (platformAdhesionType.properties.value != newValue)
                {
                    if (setValueFunction !== null)
                    {
                        setValueFunction(newValue)
                    }
                    else
                    {
                        platformAdhesionType.setPropertyValue("value", newValue)
                    }
                    forceUpdateOnChangeFunction()
                    afterOnEditingFinishedFunction()
                }
            }
        }

    }

    UM.SettingPropertyProvider
    {
        id: cultureDishNumber
        containerStack: Cura.MachineManager.activeMachine
        removeUnusedValue: false
        key: "culture_dish_number"
        watchedProperties: [ "value", "enabled" ]
        storeIndex: 0
    }
}


            