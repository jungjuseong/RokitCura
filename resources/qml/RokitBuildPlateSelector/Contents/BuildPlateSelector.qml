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
    anchors.fill: parent
    UM.I18nCatalog { id: catalog; name: "cura" }

    property var extrudersModel: Cura.ExtrudersModel {}
    property int propertyStoreIndex: manager ? manager.storeContainerIndex : 1 
    property var dishModel: {}
    property var selectedWells: "6"

    function setBuildPlateProperties(product) {
        var attr = product.plate
        if (attr != undefined) {
            buildDishWidth.setPropertyValue("value", attr.x)
            buildDishDepth.setPropertyValue("value", attr.y)
            buildDishHeight.setPropertyValue("value", attr.z)
            buildDishShape.setPropertyValue("value", dishModel.shape)
            buildDishType.setPropertyValue("value", dishModel.category + ":" + product.id)             
            buildPlateTitle.text = dishModel.category + "  -  " + product.id + " wells"
        }
    }

    Item {
        id: buildPlate
        
        height: UM.Theme.getSize("rokit_build_plate_content_widget").height
        anchors {
            left: parent.left
            right: parent.right
        } 

        Text {
            id: title
            anchors {
                bottom: comboBoxSelector.top
                left: parent.left
                leftMargin: UM.Theme.getSize("default_margin").width
                bottomMargin: UM.Theme.getSize("default_margin").width
            }
            text: catalog.i18nc("@label", "Product No.") 
            font: UM.Theme.getFont("medium")
            width: base.width / 3
        }

        Cura.ComboBox {
            id: comboBoxSelector
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
                    const dishType = buildDishType.properties.value
                    const product = dishType.split(":")[1]
                    const productId = (product.count > 1) ? product[1] : ""
                    for (var index = 0; index < model.count; index++) {
                        if (model.get(index).text === productId) {
                            return index
                        }
                    }
                    return 0   
            }
            onActivated: {
                setBuildPlateProperties(dishModel.products[index]) 
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
                            const well = dishModel.products[index]
                            switch (well.id) {
                                case "96":
                                    wellCircles.holes = [8, 12, 1/4]
                                    break
                                case "48":
                                    wellCircles.holes = [6, 8, 1/3]
                                    break
                                case "24":
                                    wellCircles.holes = [4, 6, 1/2]
                                    break
                                case "12":
                                    wellCircles.holes = [3, 4, 2/3]
                                    break
                                default: // 6
                                    wellCircles.holes = [2, 3, 1]
                            }
                            setBuildPlateProperties(well)
                        }
                    }
                }
            }
        }

        // "Build plate type"
        UM.SettingPropertyProvider {
            id: buildDishType
            containerStack: Cura.MachineManager.activeMachine
            key: "machine_build_dish_type"
            watchedProperties: [ "value" ]
            storeIndex: propertyStoreIndex
        }

        // "X (Width)"
        UM.SettingPropertyProvider {
            id: buildDishWidth
            containerStack: Cura.MachineManager.activeMachine
            key: "machine_build_dish_width"
            watchedProperties: [ "value" ]
            storeIndex: propertyStoreIndex
        }

        // "Y (Depth)"
        UM.SettingPropertyProvider {
            id: buildDishDepth
            containerStack: Cura.MachineManager.activeMachine
            key: "machine_build_dish_depth"
            watchedProperties: [ "value" ]
            storeIndex: propertyStoreIndex
        }

        // "Z (Height)"
        UM.SettingPropertyProvider {
            id: buildDishHeight
            containerStack: Cura.MachineManager.activeMachine
            key: "machine_build_dish_height"
            watchedProperties: [ "value" ]
            storeIndex: propertyStoreIndex
        }

        // MachineShape
        UM.SettingPropertyProvider {
            id: buildDishShape
            containerStack: Cura.MachineManager.activeMachine
            key: "machine_build_dish_shape"
            watchedProperties: [ "value", "options" ]
            storeIndex: propertyStoreIndex
        }
    }
}