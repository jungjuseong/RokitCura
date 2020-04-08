// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 2.3 as Controls2

import UM 1.2 as UM
import Cura 1.0 as Cura


//
//  Enable support
//
Item
{
    id: wellPlateSelector
    height: childrenRect.height //-

    property real labelColumnWidth: Math.round(width / 3)

    // 1) property is from MachineSettingsPrinterTab.qml 
    property string tooltipText: machineShape.properties.description

    // callback functions
    property var forceUpdateOnChangeFunction: dummy_func
    property var afterOnEditingFinishedFunction: dummy_func

    property var setWidthValueFunction: null
    property var setDepthValueFunction: null
    property var setHeightValueFunction: null

    // a dummy function for default property values
    function dummy_func() {}

    // 2)
    UM.I18nCatalog { id: catalog; name: "cura" }

    property int propertyStoreIndex: manager ? manager.storeContainerIndex : 1  // definition_changes

    property string machineStackId: Cura.MachineManager.activeMachine.id

    property var forceUpdateFunction: manager.forceUpdate

    Item
    {
        id: enableSupportContainer
        // 높이 핵심
        //height: enableSupportRowTitle.height *14     // edit
        height: UM.Theme.getSize("rokit_build_plate_content_widget").height

        anchors //Item place location
        {
            //left: enableSupportRowTitle.right
            left: parent.left
            right: parent.right
            //verticalCenter: enableSupportRowTitle.verticalCenter
        }  

        // Build plate Shape 확인용
        // Text{
        //     id: machineShapeView
        //     anchors{
        //         right: parent.right
        //         bottom: parent.bottom
        //         bottomMargin: 45
        //     }
        //     font: UM.Theme.getFont("large")
        //     text: qsTr(machineShape.properties.value)//+ ", "+ plateIndex)
        // }

        //Well Plate
        Rectangle   // 
        {
            id: preparingModel2

            width: childrenRect.width
            height : childrenRect.height

            anchors
            {
                // left : parent.left
                // top: parent.top
                // topMargin: UM.Theme.getsize("default_margin").width                
                // leftMargin: UM.Theme.getSize("thick_margin").width
                centerIn: parent
            }

            Column
            {
                spacing: UM.Theme.getSize("thin_margin").height // edit
                Repeater
                {
                    id : re1
                    model: 2
                    Row
                    {
                        spacing: UM.Theme.getSize("thin_margin").height // edit
                        
                        Repeater{
                            id : re2
                            model: 3

                            Rectangle{
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

        Text //Cura.IconWithText   // TEXT
        {
            id: enableSupportRowTitle   // text location
            anchors
            {            
                bottom: wellPlateButtonRow.top
                left: parent.left
                bottomMargin: UM.Theme.getSize("default_margin").width
            }
            visible: true   // edit
            text: catalog.i18nc("@label", "Number of wells") // -culture dish
            font: UM.Theme.getFont("medium")
            width: labelColumnWidth
        }

        Row{
            id: wellPlateButtonRow
            anchors
            {
                left: parent.left   // edit
                leftMargin: UM.Theme.getSize("default_margin").width
                bottom: parent.bottom
                horizontalCenter: plate1.horizontalCenter
            }
            spacing: 0.5

            ExclusiveGroup{ id: wellPlateExclusive}

            Repeater{
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
                        toCenter: 'false'
                    }
                    ListElement { 
                        text: "48"
                        plateIndex: 1
                        widthValue: 23
                        depthValue: 23
                        heightValue: 10

                        shapeValue: "elliptic"
                        toCenter: 'false'
                    }
                    ListElement { 
                        text: "24"
                        plateIndex: 2
                        widthValue: 35
                        depthValue: 35
                        heightValue: 10

                        shapeValue: "elliptic"
                        toCenter: 'false'
                    }
                    ListElement { 
                        text: "12"
                        plateIndex: 3
                        widthValue: 60
                        depthValue: 60
                        heightValue: 15

                        shapeValue: "elliptic"
                        toCenter: 'false'
                    }
                    ListElement { 
                        text: "6"
                        plateIndex: 4
                        widthValue: 90
                        depthValue: 90
                        heightValue: 15

                        shapeValue: "elliptic"
                        toCenter: 'false'
                    }
                }                

                delegate: Button{
                    
                    id: wellPlateButton
                    text: model.text
                    height: UM.Theme.getSize("rokit_well_plate_button").height
                    width: UM.Theme.getSize("rokit_well_plate_button").width
                    exclusiveGroup: wellPlateExclusive
                    checkable: true
                    
                    // contentItem: Label
                    // {
                    //     id: buttonText
                    //     text: wellPlateButton.text
                    //     color: UM.Theme.getColor("text")
                    //     font: UM.Theme.getFont("medium")
                    //     renderType: Text.NativeRendering
                    //     verticalAlignment: Text.AlignVCenter
                    //     //elide: Text.ElideRight
                    // }

                    // background: Rectangle
                    // {
                    //     id: backgroundRect
                    //     color: wellPlateButton.hovered ? UM.Theme.getColor("action_button_hovered") : "transparent"
                    //     radius: UM.Theme.getSize("action_button_radius").width
                    //     border.width: UM.Theme.getSize("default_lining").width
                    //     border.color: wellPlateButton.checked ? UM.Theme.getColor("primary") : "transparent"
                    // }

                    onClicked:
                    {
                        var newWidthValue = widthValue // width
                        var newDepthValue = depthValue // depth
                        var newHeightValue = heightValue // height
                        var newShapeValue = shapeValue // shpae
                        var newToCenter = toCenter // shpae


                        // if (machineWidth.properties.value != newWidthValue){
                        // }
                        // if (machineDepth.properties.value != newDepthValue){
                        // }
                        // if (machineHeight.properties.value != newHeightValue){
                        // }


                        if (machineShape.properties.value != newShapeValue || originAtCenter.properties.value != newToCenter)
                        {
                            if (setValueFunction !== null)
                            {
                                setValueFunction(newShapeValue)
                                setValueFunction(newToCenter)
                            }
                            else
                            {
                                machineShape.setPropertyValue("value", newShapeValue)//newValue)
                                originAtCenter.setPropertyValue("value", newToCenter)
                            }
                            forceUpdateOnChangeFunction()
                            afterOnEditingFinishedFunction()
                        }

                        //
                        if (setValueFunction !== null)
                        {
                            setWidthValueFunction(newWidthValue)
                            setDepthValueFunction(newDepthValue)
                            setHeightValueFunction(newHeightValue)
                        }
                        else
                        {
                            machineWidth.setPropertyValue("value", newWidthValue)
                            machineDepth.setPropertyValue("value", newDepthValue)
                            machineHeight.setPropertyValue("value", newHeightValue)
                        }
                        forceUpdateOnChangeFunction()
                        afterOnEditingFinishedFunction()
                    }

                    Binding //응용
                    {
                        target: supportExtruderCombobox
                        property: "currentIndex"
                        value: supportExtruderCombobox.getIndexByPosition()
                        // Sometimes when the value is already changed, the model is still being built.
                        // The when clause ensures that the current index is not updated when this happens.
                        when: supportExtruderCombobox.model.count > 0
                    }   
                }
            }
        }
    }


    // "X (Width)"
    UM.SettingPropertyProvider  
    {
        id: machineWidth
        containerStack: Cura.MachineManager.activeMachine
        key: "machine_width"
        watchedProperties: [ "value", "description" ]
        storeIndex: propertyStoreIndex
    }

    // "Y (Depth)"
    UM.SettingPropertyProvider  
    {
        id: machineDepth
        containerStack: Cura.MachineManager.activeMachine
        key: "machine_depth"
        watchedProperties: [ "value", "description" ]
        storeIndex: propertyStoreIndex
    }

    // "Z (Height)"
    UM.SettingPropertyProvider  
    {
        id: machineHeight
        containerStack: Cura.MachineManager.activeMachine
        key: "machine_height"
        watchedProperties: [ "value", "description" ]
        storeIndex: propertyStoreIndex
    }

    // MachineShape
    UM.SettingPropertyProvider
    {
        id: machineShape
        containerStack: Cura.MachineManager.activeMachine
        key: "machine_shape"
        watchedProperties: [ "value", "options", "description" ]
        storeIndex: propertyStoreIndex
        // storeIndex: 0
    }

    // "Origin at center"
    UM.SettingPropertyProvider  
    {
        id: originAtCenter
        containerStack: Cura.MachineManager.activeMachine
        key: "machine_center_is_zero"
        watchedProperties: [ "value" ]
        storeIndex: propertyStoreIndex
    }
}