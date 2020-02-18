// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 1.1

import UM 1.2 as UM
import Cura 1.0 as Cura


//
//  Culture Slide size
//
Item
{
    id: cultureSlideRow
    height: childrenRect.height

    property real labelColumnWidth: Math.round(width / 2)
    property var curaRecommendedMode: Cura.RecommendedMode {}

    Cura.IconWithText
    {
        id: cultureSlideRowTitle
        anchors { 
            top: parent.top
            left: parent.left
        }
        source: UM.Theme.getIcon("hollow")
        text: catalog.i18nc("@label", "Culture slide")
        font: UM.Theme.getFont("medium")
        width: labelColumnWidth
    }

    Item
    {
        id: cultureSlideContainer

        property int controlWidth: UM.Theme.getSize("setting_control").width
        property int controlHeight: UM.Theme.getSize("setting_control").height

        height: cultureSlideComboBox.height

        anchors
        {
            top: parent.top

            left: cultureSlideRowTitle.right
            right: parent.right
            verticalCenter: cultureSlideRowTitle.verticalCenter
        }

        Cura.ComboBox
        {

            id: cultureSlideComboBox
            anchors {
                left: fieldLabel.right
                leftMargin: UM.Theme.getSize("default_margin").width
            }
            width: cultureSlideContainer.controlWidth
            height: cultureSlideContainer.controlHeight
            model: ListModel {
                id: model
                ListElement { text: "100090"; color: "Orange" }
                ListElement { text: "100060"; color: "Orange" }
                ListElement { text: "100035"; color: "Orange" }
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
        id: platformAdhesionType
        containerStack: Cura.MachineManager.activeMachine
        removeUnusedValue: false //Doesn't work with settings that are resolved.
        key: "adhesion_type"
        watchedProperties: [ "value", "resolve", "enabled" ]
        storeIndex: 0
    }
}


            