// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 2.3 as Controls2

import UM 1.2 as UM
import Cura 1.0 as Cura

//
import QtQuick.Layouts 1.3

import "../../Widgets"


//
//  Enable support
//
Item
{
    id: cultureSliderSelector
    
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
        //height: UM.Theme.getSize("preparing_setup_widget").height
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

        // Build plate 
        // Text{
        //     id: machineShapeView
        //     anchors{
        //         right: parent.right
        //         bottom: parent.bottom
        //         bottomMargin: 45
        //     }
        //     font: UM.Theme.getFont("large")
        //     text: qsTr(buildPlateType.properties.value)//+ ", "+ plateIndex)
        // }

        //Culture Slide
        Rectangle 
        {
            id: preparingModel3

            width: UM.Theme.getSize("rokit_culture_slide").width // culture dish's diameter
            height : UM.Theme.getSize("rokit_culture_slide").height
            
            anchors
            {
                // left : parent.left
                // top: parent.top
                // topMargin: UM.Theme.getsize("default_margin").width                
                // leftMargin: UM.Theme.getSize("thick_margin").width
                centerIn: parent
            }

            visible : true
            color: UM.Theme.getColor("rokit_build_plate")

            border.width : 1
            border.color: UM.Theme.getColor("rokit_build_plate_border")
        }


        Text //Cura.IconWithText   // TEXT
        {
            id: enableSupportRowTitle   // text location
            anchors
            {
                bottom: cultureSlideCombobox.top
                left: parent.left
                bottomMargin: UM.Theme.getSize("default_margin").width
            }
            visible: true   // edit
            text: catalog.i18nc("@label", "Size(mm)") // -culture slide
            font: UM.Theme.getFont("medium")
            width: labelColumnWidth
        }

        Cura.ComboBox
        {
            id: cultureSlideCombobox

            height: UM.Theme.getSize("rokit_combobox_default").height
            width: UM.Theme.getSize("rokit_combobox_default").width
            anchors
            {
                left: parent.left   // edit
                //right: parent.right
                bottom: parent.bottom                
                leftMargin: UM.Theme.getSize("default_margin").width
                //rightMargin: UM.Theme.getSize("thick_margin").width
                //verticalCenter: plate1.verticalCenter
                horizontalCenter: plate1.horizontalCenter
            }

            // Text{
            //     id: firstText
            //     text: qsTr(cultureSlideCombobox.model.get(index).plateIndex)
            //     anchors.centerIn: parent
            //     visible: currentIndex == -1
            // }

            enabled: true
            visible: true
            textRole: "text"  // this solves that the combobox isn't populated in the first time Cura is started

            model: ListModel 
            {
                id: plateModel

                ListElement { 
                    text: "3800052CL" 
                    plateIndex: 0
                    widthValue: 25
                    depthValue: 50
                    heightValue: 10

                    shapeValue: "rectangular"
                    index: 0
                    toCenter: 'true'
                }
                ListElement { 
                    text: "3800056CL" 
                    plateIndex: 1
                    widthValue: 20
                    depthValue: 40
                    heightValue: 10

                    shapeValue: "rectangular"
                    index: 1
                    toCenter: 'true'
                }

                ListElement { 
                    text: "3800058CL" 
                    plateIndex: 2
                    widthValue: 15
                    depthValue: 30
                    heightValue: 10

                    shapeValue: "rectangular"
                    index: 2
                    toCenter: 'true'
                }
            }

            currentIndex: 
            {
                var currentValue = machineShape.properties.value
                var index = 0 // to reset the selection
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

            function getIndexByPosition()
            {
                var itemIndex = -1  // if position is not found, return -1
                return itemIndex
            }     
            
            onActivated:
            {
                var newWidthValue = model.get(index).widthValue // width
                var newDepthValue = model.get(index).depthValue // depth
                var newHeightValue = model.get(index).heightValue // height
                var newShapeValue = model.get(index).shapeValue // shpae
                var newToCenter = model.get(index).toCenter // shpae
                var cultureSlideNum = model.get(index).text // shpae

                buildPlateType.setPropertyValue("value", "Culture Slide")
                cultureSlideNumber.setPropertyValue("value", cultureSlideNum)
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
                        machineShape.setPropertyValue("value", newShapeValue) //newValue)
                        originAtCenter.setPropertyValue("value", newToCenter)
                    }
                    forceUpdateOnChangeFunction()
                    afterOnEditingFinishedFunction()
                }

                // setValue 
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

                // ???
                forceUpdateOnChangeFunction()
                afterOnEditingFinishedFunction()
            }

            Binding //응용
            {
                target: cultureSlideCombobox
                property: "currentIndex"
                value: cultureSlideCombobox.getIndexByPosition()
                // Sometimes when the value is already changed, the model is still being built.
                // The when clause ensures that the current index is not updated when this happens.
                when: cultureSlideCombobox.model.count > 0
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

    // "Build plate type"
    UM.SettingPropertyProvider  
    {
        id: buildPlateType
        containerStack: Cura.MachineManager.activeMachine
        key: "build_plate_type"
        watchedProperties: [ "value", "options" ]
        storeIndex: propertyStoreIndex
    }

    // "Culture Slide Num"
    UM.SettingPropertyProvider  
    {
        id: cultureSlideNumber
        containerStack: Cura.MachineManager.activeMachine
        key: "culture_slide_category_number"
        watchedProperties: [ "value", "options" ]
        storeIndex: propertyStoreIndex
    }
}