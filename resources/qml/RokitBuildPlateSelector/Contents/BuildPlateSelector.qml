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

Item {
    id: buildPlate
    
    height: UM.Theme.getSize("rokit_build_plate_content_widget").height

    property int propertyStoreIndex: manager ? manager.storeContainerIndex : 1 
    property var dishModel: {}

    function setBuildPlateProperties(productId, attributes) {  

        machineWidth.setPropertyValue("value", attributes.x)
        machineDepth.setPropertyValue("value", attributes.y)
        machineHeight.setPropertyValue("value", attributes.z)
        machineShape.setPropertyValue("value", dishModel.shape)

        buildPlateType.setPropertyValue("value", dishModel.category + ":" + productId)             
        buildPlateTitle.text = dishModel.category + "  -  " + productId 
    }

    UM.I18nCatalog { id: catalog; name: "cura" }

    anchors {
        left: parent.left
        right: parent.right
    } 

    Text {
        id: title
        anchors {
            bottom: comboboxSelector.top
            left: parent.left
            leftMargin: UM.Theme.getSize("default_margin").width
            bottomMargin: UM.Theme.getSize("default_margin").width
        }
        text: catalog.i18nc("@label", "Product No.") 
        font: UM.Theme.getFont("medium")
        width: base.width / 3
    }

    Cura.ComboBox {
        id: comboboxSelector
        visible: dishModel.category !== "Well Plate"

        height: UM.Theme.getSize("rokit_combobox_default").height
        width: UM.Theme.getSize("rokit_combobox_default").width
        anchors  {
            left: parent.left 
            bottom: parent.bottom                
            leftMargin: UM.Theme.getSize("default_margin").width
        }
        textRole: "text"  // this solves that the combobox isn't populated in the first time Cura is started

        model: dishModel

        currentIndex: {
                const productId = buildPlateType.properties.value.split(":")[1]
                if (productId !== undefined) {
                    for (var i = 0; i < model.count; i++) {
                        if (model.get(i).text === productId) {
                            return i
                        }
                    }
                }
                return 0   
        }
        onActivated: { 
            setBuildPlateProperties(model.get(index).text, dishModel.attributes[index]) 
        }
    }
    
    Item {
        id: buttonSelector
        visible: dishModel.category === "Well Plate"

        height: UM.Theme.getSize("rokit_well_plate_button").height
        width: UM.Theme.getSize("rokit_well_plate_button").width
        anchors  {
            left: parent.left 
            bottom: parent.bottom                
            leftMargin: UM.Theme.getSize("default_margin").width
        }

        Row {
            spacing: 0.5
            ExclusiveGroup { id: buttonExclusive }
            Repeater {
                model: dishModel

                delegate: Button {                    
                    text: model.text
                    height: UM.Theme.getSize("rokit_well_plate_button").height
                    width: UM.Theme.getSize("rokit_well_plate_button").width
                    exclusiveGroup: buttonExclusive
                    checkable: true
                    
                    onClicked: { 
                        setBuildPlateProperties(model.text, dishModel.attributes[index]) 
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