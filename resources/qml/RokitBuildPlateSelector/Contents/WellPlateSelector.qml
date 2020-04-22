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
<<<<<<< HEAD

=======
        
>>>>>>> d91739bfc7542d5a315dd0b12dd5a79260a434b7
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
<<<<<<< HEAD
                model: WellPlateModel {
                    id: wellPlateModel
                }            
=======
                model: ListModel 
                {
                    id: model
                    ListElement { 
                        text: "96"
                        plateIndex: 0
                        widthValue: 20
                        depthValue: 20
                        heightValue: 10

                        shapeValue: "elliptic"
                    }
                    ListElement { 
                        text: "48"
                        plateIndex: 1
                        widthValue: 23
                        depthValue: 23
                        heightValue: 10

                        shapeValue: "elliptic"
                    }
                    ListElement { 
                        text: "24"
                        plateIndex: 2
                        widthValue: 35
                        depthValue: 35
                        heightValue: 10

                        shapeValue: "elliptic"
                    }
                    ListElement { 
                        text: "12"
                        plateIndex: 3
                        widthValue: 60
                        depthValue: 60
                        heightValue: 15

                        shapeValue: "elliptic"
                    }
                    ListElement { 
                        text: "6"
                        plateIndex: 4
                        widthValue: 90
                        depthValue: 90
                        heightValue: 15

                        shapeValue: "elliptic"
                    }
                }                
>>>>>>> d91739bfc7542d5a315dd0b12dd5a79260a434b7

                delegate: Button {                    
                    text: model.text
                    height: UM.Theme.getSize("rokit_well_plate_button").height
                    width: UM.Theme.getSize("rokit_well_plate_button").width
                    exclusiveGroup: wellPlateExclusive
                    checkable: true
<<<<<<< HEAD
                    
                    onClicked: {
                        var productNo = text
                        var attributes = wellPlateModel.attributes[index]
=======
                
                    onClicked:
                    {
                        var newWidthValue = widthValue // width
                        var newDepthValue = depthValue // depth
                        var newHeightValue = heightValue // height
                        var newShapeValue = shapeValue // shpae
                        var wellPlateNum = text

                        buildPlateType.setPropertyValue("value", "Well Plate")
                        wellPlateNumber.setPropertyValue("value", wellPlateNum)

                        // 1) 모양, 센터, 플레이트 네임 설정
                        if (machineShape.properties.value != newShapeValue)
                        {
                            if (setValueFunction !== null)
                            {
                                setValueFunction(newShapeValue)
                            
                            }
                            else
                            {
                                machineShape.setPropertyValue("value", newShapeValue)
\                            }
                            forceUpdateOnChangeFunction()
                            afterOnEditingFinishedFunction()
                        }
>>>>>>> d91739bfc7542d5a315dd0b12dd5a79260a434b7

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
<<<<<<< HEAD
                    }  
=======
                    } 
>>>>>>> d91739bfc7542d5a315dd0b12dd5a79260a434b7
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
<<<<<<< HEAD
=======
        watchedProperties: [ "value", "options", "description" ]
        storeIndex: propertyStoreIndex
        // storeIndex: 0
    }

    // "Build plate type"
    UM.SettingPropertyProvider  
    {
        id: buildPlateType
        containerStack: Cura.MachineManager.activeMachine
        key: "build_plate_type"
        watchedProperties: [ "value", "options" ]
        storeIndex: propertyStoreIndex
    }

    // "Well plate Number"
    UM.SettingPropertyProvider  
    {
        id: wellPlateNumber
        containerStack: Cura.MachineManager.activeMachine
        key: "well_plate_number"
>>>>>>> d91739bfc7542d5a315dd0b12dd5a79260a434b7
        watchedProperties: [ "value", "options" ]
        storeIndex: propertyStoreIndex
        // storeIndex: 0
    }
}