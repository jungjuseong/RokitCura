// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 2.3 as Controls2

import UM 1.2 as UM
import Cura 1.0 as Cura
import QtQuick.Layouts 1.3

import "../../Widgets"
import "./model"

//
//  Culture Slide
//
Item {
    id: cultureSliderSelector
    
    height: childrenRect.height //-

    property real labelColumnWidth: Math.round(width / 3)    

    property int propertyStoreIndex: manager ? manager.storeContainerIndex : 1
    property var forceUpdateFunction: manager.forceUpdate

    property string machineStackId: Cura.MachineManager.activeMachine.id

    property string tooltipText: machineShape.properties.description

    // callback functions
    property var forceUpdateOnChangeFunction: forceUpdateFunction
    property var afterOnEditingFinishedFunction: dummy_func

    // a dummy function for default property values
    function dummy_func() {}

    // 2)

    Item  {
        id: cultureSlideContainer
        UM.I18nCatalog { id: catalog; name: "cura" }

        height: UM.Theme.getSize("rokit_build_plate_content_widget").height
        
        anchors
        {
            left: parent.left
            right: parent.right
        }       
        
        Rectangle {
            id: preparingModel3

            width: UM.Theme.getSize("rokit_culture_slide").width
            height : UM.Theme.getSize("rokit_culture_slide").height
            
            anchors
            {
                centerIn: parent
            }

            visible : true
            color: UM.Theme.getColor("rokit_build_plate")

            border.width : 1
            border.color: UM.Theme.getColor("rokit_build_plate_border")
        }


        Text {
            id: enableSupportRowTitle 
            anchors {
                bottom: cultureSlideCombobox.top
                left: parent.left
                leftMargin: UM.Theme.getSize("default_margin").width
                bottomMargin: UM.Theme.getSize("default_margin").width
            }
            text: catalog.i18nc("@label", "Size(mm)")
            font: UM.Theme.getFont("medium")
            width: labelColumnWidth
        }

        Cura.ComboBox {
            id: cultureSlideCombobox

            height: UM.Theme.getSize("rokit_combobox_default").height
            width: UM.Theme.getSize("rokit_combobox_default").width
            anchors  {
                left: parent.left
                bottom: parent.bottom                
                leftMargin: UM.Theme.getSize("default_margin").width

                horizontalCenter: plate1.horizontalCenter
            }

            enabled: true
            textRole: "text" 

            model: CultureSlideModel {
                id: cultureSlideModel
            }  
            
            onActivated: {
                var productNo = model.get(index).text 
                var attributes = cultureSlideModel.attributes[index]

                buildPlateType.setPropertyValue("value", "Culture Slide:" + productNo)

                if (machineShape.properties.value !== attributes.shape) {
                    machineShape.setPropertyValue("value", attributes.shape) 
                }

                machineWidth.setPropertyValue("value", attributes.widh)
                machineDepth.setPropertyValue("value", attributes.depth)
                machineHeight.setPropertyValue("value", attributes.height)                       

                forceUpdateOnChangeFunction()
                afterOnEditingFinishedFunction()
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

    // "Build plate type"
    UM.SettingPropertyProvider  
    {
        id: buildPlateType
        containerStack: Cura.MachineManager.activeMachine
        key: "machine_buildplate_type"
        watchedProperties: [ "value", "options" ]
        storeIndex: propertyStoreIndex
    }
}