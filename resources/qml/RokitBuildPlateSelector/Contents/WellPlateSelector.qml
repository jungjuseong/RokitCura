// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 2.3 as Controls2

import UM 1.2 as UM
import Cura 1.0 as Cura

import "./model"

//  Well Plate

Item {
    id: wellPlateSelector
    height: childrenRect.height

    property real labelColumnWidth: Math.round(width / 3)

    property int propertyStoreIndex: manager ? manager.storeContainerIndex : 1 
    property var forceUpdateFunction: manager.forceUpdate

    property string machineStackId: Cura.MachineManager.activeMachine.id

    property var forceUpdateOnChangeFunction: dummy_func
    property var afterOnEditingFinishedFunction: dummy_func

    function dummy_func() {}

    Item
    {
        id: wellPlateContainer

        UM.I18nCatalog { id: catalog; name: "cura" }

        height: UM.Theme.getSize("rokit_build_plate_content_widget").height
        anchors
        {
            left: parent.left
            right: parent.right
        }  
        //Well Plate
        Rectangle {
            id: preparingModel2

            width: childrenRect.width
            height : childrenRect.height

            anchors { centerIn: parent }

            Column {
                spacing: UM.Theme.getSize("thin_margin").height
                Repeater {
                    model: 2
                    Row {
                        spacing: UM.Theme.getSize("thin_margin").height 
                        
                        Repeater {
                            model: 3

                            Rectangle {
                                width : UM.Theme.getSize("rokit_well_plate_diameter").width
                                height : width

                                visible : true
                                radius: width*0.5
                                color: UM.Theme.getColor("rokit_build_plate")

                                border.width : 1
                                border.color: UM.Theme.getColor("rokit_build_plate_border")
                            }
                        }                  
                    }
                }
            }
        }

        Text  {
            anchors {            
                bottom: wellPlateButtons.top
                left: parent.left
                bottomMargin: UM.Theme.getSize("default_margin").width
            }
            text: catalog.i18nc("@label", "Number of Wells")
            font: UM.Theme.getFont("medium")
            width: labelColumnWidth
        }

        Row {
            id: wellPlateButtons
            anchors
            {
                left: parent.left
                leftMargin: UM.Theme.getSize("default_margin").width
                bottom: parent.bottom
                horizontalCenter: plate1.horizontalCenter
            }
            spacing: 0.5

            ExclusiveGroup{ id: wellPlateExclusive}
   

            Repeater{
                model: WellPlateModel {
                    id: wellPlateModel
                }            

                delegate: Button {                    
                    text: model.text
                    height: UM.Theme.getSize("rokit_well_plate_button").height
                    width: UM.Theme.getSize("rokit_well_plate_button").width
                    exclusiveGroup: wellPlateExclusive
                    checkable: true
                    
                    onClicked: {
                        var productNo = text
                        var attributes = wellPlateModel.attributes[index]

                        buildPlateType.setPropertyValue("value", "Well Plate:" + productNo)

                        if (machineShape.properties.value !== attributes.shape)
                        {
                            machineShape.setPropertyValue("value", attributes.shape)
                        }
                        
                        machineWidth.setPropertyValue("value", attributes.width)
                        machineDepth.setPropertyValue("value", attributes.depth)
                        machineHeight.setPropertyValue("value", attributes.height)

                        forceUpdateOnChangeFunction()
                        afterOnEditingFinishedFunction()
                    }  
                }
            }
        }
    }

    // "Build plate type"
    UM.SettingPropertyProvider {
        id: buildPlateType
        containerStack: Cura.MachineManager.activeMachine
        key: "machine_buildplate_type"
        watchedProperties: [ "value", "options" ]
        storeIndex: propertyStoreIndex
    }

    // "X (Width)"
    UM.SettingPropertyProvider {
        id: machineWidth
        containerStack: Cura.MachineManager.activeMachine
        key: "machine_width"
        watchedProperties: [ "value" ]
        storeIndex: propertyStoreIndex
    }

    // "Y (Depth)"
    UM.SettingPropertyProvider {
        id: machineDepth
        containerStack: Cura.MachineManager.activeMachine
        key: "machine_depth"
        watchedProperties: [ "value" ]
        storeIndex: propertyStoreIndex
    }

    // "Z (Height)"
    UM.SettingPropertyProvider {
        id: machineHeight
        containerStack: Cura.MachineManager.activeMachine
        key: "machine_height"
        watchedProperties: [ "value" ]
        storeIndex: propertyStoreIndex
    }

    // MachineShape
    UM.SettingPropertyProvider {
        id: machineShape
        containerStack: Cura.MachineManager.activeMachine
        key: "machine_shape"
        watchedProperties: [ "value", "options" ]
        storeIndex: propertyStoreIndex
        // storeIndex: 0
    }
}