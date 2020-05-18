// Copyright (c) 2019 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.6
import QtQuick.Controls 2.0
import QtQuick.Controls 1.1 as OldControls
import QtQuick.Layouts 1.3

import Cura 1.0 as Cura
import UM 1.3 as UM

Cura.MachineAction {
    id: base

    UM.I18nCatalog { id: catalog;  name: "cura" }

    width: parent.width
    height: childrenRect.height
    
    property int propertyStoreIndex: manager ? manager.storeContainerIndex : 1

    property int controlHeight: UM.Theme.getSize("setting_control").height * 1.2
    property var labelFont: UM.Theme.getFont("default")

    property string machineStackId: Cura.MachineManager.activeMachine.id
    property var extrudersModel:  CuraApplication.getExtrudersModel()

    function getActiveExtruderId() {
        const activeExtruder = CuraApplication.getExtrudersModel().getItem(tabBar.currentIndex)
        return (activeExtruder != null) ? activeExtruder.id : "None"
    }

    function getActiveExtruderName() {
        const activeExtruder = CuraApplication.getExtrudersModel().getItem(tabBar.currentIndex)
        return (activeExtruder != null)  ? activeExtruder.name : "None"
    }

    function getExtruderType() {
        const variantName = Cura.MachineManager.activeStack.variant.name
        const lists = variantName.split(" ")
        if (lists.length > 0)
            return lists[1]
        
        return ""
    }

    // "Build dish type"
    UM.SettingPropertyProvider {
        id: buildDishType
        containerStack: Cura.MachineManager.activeMachine
        key: "machine_build_dish_type"
        watchedProperties: [ "value"]
        storeIndex: propertyStoreIndex
    }

    Label {
        id: header
        text: {
                if (buildDishType.properties.value == null || buildDishType.properties.value == undefined) {
                    return catalog.i18nc("@header", "Generation")
                }
                const buildDish = buildDishType.properties.value.split(":")

                return "Build Plate: " + buildDish[0] + " - " + buildDish[1]
        }
        font: UM.Theme.getFont("medium")
        color: UM.Theme.getColor("small_button_text")
        height: contentHeight
        renderType: Text.NativeRendering

        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
        }
    }


    UM.TabRow {
        id: tabBar
        anchors.top: header.bottom
        anchors.topMargin: UM.Theme.getSize("default_margin").height
        visible: extrudersModel.count > 1

        Repeater {
            id: repeater
            model: extrudersModel
            delegate: UM.TabRowButton {
                contentItem: Item {
                    Cura.RokitExtruderIcon {
                        anchors.horizontalCenter: parent.horizontalCenter
                        materialColor: model.color
                        width: parent.height
                        height: parent.height
                    }
                }
                onClicked: {
                    Cura.ExtruderManager.setActiveExtruderIndex(tabBar.currentIndex)
                }
            }
        }
    }

    Rectangle {
        width: parent.width
        height: childrenRect.height
        anchors.top: tabBar.bottom

        radius: tabBar.visible ? UM.Theme.getSize("default_radius").width : 0
        border.width: tabBar.visible ? UM.Theme.getSize("default_lining").width : 0
        border.color: UM.Theme.getColor("lining")
        color: UM.Theme.getColor("main_background")

        //Remove rounding and lining at the top.
        Rectangle {
            width: parent.width
            height: parent.radius
            anchors.top: parent.top
            color: UM.Theme.getColor("lining")
            visible: tabBar.visible
            Rectangle {
                anchors {
                    left: parent.left
                    leftMargin: parent.parent.border.width
                    right: parent.right
                    rightMargin: parent.parent.border.width
                    top: parent.top
                }
                height: parent.parent.radius
                color: parent.parent.color
            }
        }

        Column {
            id: selectors

            padding: UM.Theme.getSize("default_margin").width
            spacing: UM.Theme.getSize("default_margin").height / 5

            readonly property real paddedWidth: parent.width - padding
            property real textWidth: Math.round(paddedWidth * 0.2)
            property real controlWidth: (paddedWidth - textWidth - UM.Theme.getSize("print_setup_big_item").height * 0.5 - UM.Theme.getSize("default_margin").width) / 3.2

            readonly property real bar_width: UM.Theme.getSize("rokit_big_item").width
            readonly property real bar_height: UM.Theme.getSize("rokit_big_item").height * 0.8
            readonly property real bar_radius: UM.Theme.getSize("rokit_combobox_radius").height

            readonly property var bar_border_color: UM.Theme.getColor("setting_control_border")
            readonly property var bar_color: UM.Theme.getColor("secondary_shadow")

            Cura.ObjectsModel {id: objectsModel }

            Row { // Object list Bar
                visible: objectsModel.count > 0
                Rectangle {
                    width: selectors.bar_width
                    height: selectors.bar_height
                    radius: selectors.bar_radius
                    color: selectors.bar_color
                    border.color: selectors.bar_border_color

                    anchors { 
                        margins: UM.Theme.getSize("default_margin").width
                    }

                    Text {
                        anchors{
                            verticalCenter: parent.verticalCenter
                            left: parent.left
                            leftMargin: UM.Theme.getSize("default_margin").width 
                        }
                        text: objectsModel.getItem(0).name + ((objectsModel.count > 1) ? " ..." : "")
                    }
                }
            }

            Row { // Material Configuration Bar
                visible: Cura.MachineManager.activeMachine.hasMaterials
                Rectangle {
                    width: selectors.bar_width
                    height: selectors.bar_height
                    radius: selectors.bar_radius
                    color: selectors.bar_color
                    border.color: selectors.bar_border_color

                    anchors { 
                        margins: UM.Theme.getSize("default_margin").width
                    }

                    Text {
                        anchors{
                            verticalCenter: parent.verticalCenter
                            left: parent.left
                            leftMargin: UM.Theme.getSize("default_margin").width 
                        }
                        text:  Cura.MachineManager.activeStack.variant.name + " - " + Cura.MachineManager.activeStack.material.name
                    }
                }
            }

            Row { // Nozzle Guage
                visible: !Cura.MachineManager.activeMachine.hasMaterials
                Label {
                    text: (getActiveExtruderName() === "Left") ? Cura.MachineManager.activeDefinitionVariantsName : "Needle Guage"
                    verticalAlignment: Text.AlignVCenter
                    font: base.labelFont
                    color: UM.Theme.getColor("text")
                    height: parent.height
                    width: base.textWidth
                    renderType: Text.NativeRendering
                }
                ToolButton {
                    text: Cura.MachineManager.activeStack != null ? Cura.MachineManager.activeStack.variant.name : ""
                    width: selectors.controlWidth
                    height: parent.height
                }
            }

            Row { // Material
                visible: !Cura.MachineManager.activeMachine.hasMaterials
                Label {
                    text: catalog.i18nc("@label", "Material")
                    verticalAlignment: Text.AlignVCenter
                    font: base.labelFont
                    color: UM.Theme.getColor("text")
                    height: parent.height
                    width: base.textWidth
                    renderType: Text.NativeRendering
                }
                ToolButton {
                    text: Cura.MachineManager.activeStack !== null ? Cura.MachineManager.activeStack.material.name : ""
                    width: selectors.controlWidth
                    height: parent.height
                }
            }

            GridLayout {
                id: material

                Layout.fillWidth: true
                columnSpacing: 24 * screenScaleFactor
                rowSpacing: 1 * screenScaleFactor
                anchors {
                    //top: materialBar.bottom
                    left: selectors.left
                    margins: UM.Theme.getSize("default_margin").width
                }

                columns: 2

                Cura.NumericTextFieldWithUnit {
                    containerStackId: getActiveExtruderId()
                    settingKey: "material_print_temperature"
                    labelText: catalog.i18nc("@label", "Print Temp.")
                    unitText: catalog.i18nc("@label", "°C")

                    labelFont: base.labelFont
                    labelWidth: selectors.textWidth
                    controlWidth: selectors.controlWidth
                    controlHeight: base.controlHeight
                    textField.readOnly: true
                }
                Cura.NumericTextFieldWithUnit {
                    containerStackId: getActiveExtruderId()
                    settingKey: "material_bed_temperature"
                    labelText: catalog.i18nc("@label", "Bed Temp.")
                    unitText: catalog.i18nc("@label", "°C")

                    labelFont: base.labelFont
                    labelWidth: selectors.textWidth
                    controlWidth: selectors.controlWidth
                    controlHeight: base.controlHeight
                    textField.readOnly: true
                }
             
            }

            Row { // Layer Quality Bar
                visible: Cura.MachineManager.activeMachine.hasMaterials
                Rectangle {
                    width: selectors.bar_width
                    height: selectors.bar_height
                    radius: selectors.bar_radius
                    color: selectors.bar_color
                    border.color: selectors.bar_border_color
                    
                    anchors { 
                        margins: UM.Theme.getSize("default_margin").width
                    }

                    Text {
                        anchors{
                            verticalCenter: parent.verticalCenter
                            left: parent.left
                            leftMargin: UM.Theme.getSize("default_margin").width 
                        }
                        text: "Layer Quality"
                    }
                }
            }

            GridLayout {
                id: layer

                Layout.fillWidth: true
                columnSpacing: 24 * screenScaleFactor
                rowSpacing: 1 * screenScaleFactor
                anchors {
                    left: selectors.left
                    margins: UM.Theme.getSize("default_margin").width
                }

                columns: 2

                Cura.NumericTextFieldWithUnit {
                    containerStackId: getActiveExtruderId()
                    settingKey: "layer_height"
                    labelText: catalog.i18nc("@label", "Layer Height")
                    unitText: catalog.i18nc("@label", "mm")

                    labelFont: base.labelFont
                    labelWidth: selectors.textWidth
                    controlWidth: selectors.controlWidth
                    controlHeight: base.controlHeight
                    textField.readOnly: true
                }

                Cura.NumericTextFieldWithUnit {
                    containerStackId: getActiveExtruderId()
                    settingKey: "infill_pattern"
                    labelText: catalog.i18nc("@label", "Infill Pattern")

                    labelFont: base.labelFont
                    labelWidth: selectors.textWidth
                    controlWidth: selectors.controlWidth
                    controlHeight: base.controlHeight
                    textField.readOnly: true
                }

                Cura.NumericTextFieldWithUnit {
                    containerStackId: getActiveExtruderId()
                    settingKey: "infill_sparse_density"
                    labelText: catalog.i18nc("@label", "Infill Density")
                    unitText: catalog.i18nc("@label", "%")

                    labelFont: base.labelFont
                    labelWidth: selectors.textWidth
                    controlWidth: selectors.controlWidth
                    controlHeight: base.controlHeight
                    textField.readOnly: true
                }
            }

            Row { // UV Bar
                visible: Cura.MachineManager.activeMachine.hasMaterials
                Rectangle {
                    width: selectors.bar_width
                    height: selectors.bar_height
                    border.color: selectors.bar_border_color
                    radius: selectors.bar_radius 
                    color: selectors.bar_color
                    anchors { 
                        margins: UM.Theme.getSize("default_margin").width
                    }

                    Text {
                        anchors{
                            verticalCenter: parent.verticalCenter
                            left: parent.left
                            leftMargin: UM.Theme.getSize("default_margin").width 
                        }
                        text: "UV"
                    }
                }
                
            }

            GridLayout {
                id: uv

                Layout.fillWidth: true
                columnSpacing: 24 * screenScaleFactor
                rowSpacing: 1 * screenScaleFactor
                anchors {
                    left: selectors.left
                    margins: UM.Theme.getSize("default_margin").width
                }

                columns: 2

                Cura.NumericTextFieldWithUnit  {
                    containerStackId: getActiveExtruderId()
                    settingKey: "uv_per_layers"
                    labelText: catalog.i18nc("@label", "Layers")
                    unitText: catalog.i18nc("@label", "layers")

                    labelFont: base.labelFont
                    labelWidth: selectors.textWidth
                    controlWidth: selectors.controlWidth
                    controlHeight: base.controlHeight
                    textField.readOnly: true
                }

                Cura.NumericTextFieldWithUnit  {
                    containerStackId: getActiveExtruderId()
                    settingKey: "uv_type"
                    labelText: catalog.i18nc("@label", "Type")
                    unitText: catalog.i18nc("@label", "nm")

                    labelFont: base.labelFont
                    labelWidth: selectors.textWidth
                    controlWidth: selectors.controlWidth
                    controlHeight: base.controlHeight
                    textField.readOnly: true
                }

                Cura.NumericTextFieldWithUnit {
                    containerStackId: getActiveExtruderId()
                    settingKey: "uv_time"
                    labelText: catalog.i18nc("@label", "Time")
                    unitText: catalog.i18nc("@label", "sec")

                    labelFont: base.labelFont
                    labelWidth: selectors.textWidth
                    controlWidth: selectors.controlWidth
                    controlHeight: base.controlHeight
                    textField.readOnly: true
                }

                Cura.NumericTextFieldWithUnit {
                    containerStackId: getActiveExtruderId()
                    settingKey: "uv_dimming"
                    labelText: catalog.i18nc("@label", "Dimming")
                    unitText: catalog.i18nc("@label", "%")

                    labelFont: base.labelFont
                    labelWidth: selectors.textWidth
                    controlWidth: selectors.controlWidth
                    controlHeight: base.controlHeight
                    textField.readOnly: true
                }
            }

            Row { // Dispensor Bar
                visible: getExtruderType() === "Syringe"
                Rectangle {
                    width:  selectors.bar_width
                    height: selectors.bar_height
                    border.color: selectors.bar_border_color
                    radius: selectors.bar_radius 
                    color: selectors.bar_color
                    anchors { 
                        margins: UM.Theme.getSize("default_margin").width
                    }

                    Text {
                        anchors {
                            verticalCenter: parent.verticalCenter
                            left: parent.left
                            leftMargin: UM.Theme.getSize("default_margin").width 
                        }
                        text: "Dispensor"
                    }
                }
            }

            GridLayout {
                id: dispensor

                visible: getExtruderType() === "Syringe"

                Layout.fillWidth: true
                columnSpacing: 24 * screenScaleFactor
                rowSpacing: 1 * screenScaleFactor
                anchors {
                    left: selectors.left
                    margins: UM.Theme.getSize("default_margin").width
                }
                
                columns: 2

                Cura.NumericTextFieldWithUnit {
                    containerStackId: getActiveExtruderId()
                    settingKey: "dispensor_shot"
                    labelText: catalog.i18nc("@label", "SHOT")
                    unitText: catalog.i18nc("@label", "sec")

                    labelFont: base.labelFont
                    labelWidth: selectors.textWidth
                    controlWidth: selectors.controlWidth
                    controlHeight: base.controlHeight
                    textField.readOnly: true
                }                

                Cura.NumericTextFieldWithUnit {
                    containerStackId: getActiveExtruderId()
                    settingKey: "dispensor_vac"
                    labelText: catalog.i18nc("@label", "VAC")
                    unitText: catalog.i18nc("@label", "sec")

                    labelFont: base.labelFont
                    labelWidth: selectors.textWidth
                    controlWidth: selectors.controlWidth
                    controlHeight: base.controlHeight
                    textField.readOnly: true
                }

                Cura.NumericTextFieldWithUnit {
                    containerStackId: getActiveExtruderId()
                    settingKey: "dispensor_int"
                    labelText: catalog.i18nc("@label", "INT")
                    unitText: catalog.i18nc("@label", "kpa")

                    labelFont: base.labelFont
                    labelWidth: selectors.textWidth
                    controlWidth: selectors.controlWidth
                    controlHeight: base.controlHeight
                    textField.readOnly: true
                }                

                Cura.NumericTextFieldWithUnit {
                    containerStackId: getActiveExtruderId()
                    settingKey: "dispensor_shot_power"
                    labelText: catalog.i18nc("@label", "SHOT P.")
                    unitText: catalog.i18nc("@label", "kpa")

                    labelFont: base.labelFont
                    labelWidth: selectors.textWidth
                    controlWidth: selectors.controlWidth
                    controlHeight: base.controlHeight
                    textField.readOnly: true
                }

                Cura.NumericTextFieldWithUnit {
                    containerStackId: getActiveExtruderId()
                    settingKey: "dispensor_vac_power"
                    labelText: catalog.i18nc("@label", "VAC P.")

                    unitText: catalog.i18nc("@label", "kpa")
                    labelFont: base.labelFont
                    labelWidth: selectors.textWidth
                    controlWidth: selectors.controlWidth
                    controlHeight: base.controlHeight
                    textField.readOnly: true
                }
                
            }
            
        }
    }

}
