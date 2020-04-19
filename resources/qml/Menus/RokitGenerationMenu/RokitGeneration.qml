// Copyright (c) 2019 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.6
import QtQuick.Controls 2.0
import QtQuick.Controls 1.1 as OldControls
import QtQuick.Layouts 1.3

import Cura 1.0 as Cura
import UM 1.3 as UM

Item
{
    id: base

    UM.I18nCatalog { id: catalog;  name: "cura" }

    width: parent.width
    height: childrenRect.height
    
    property int propertyStoreIndex: manager ? manager.storeContainerIndex : 1  // definition_changes

    property int controlHeight: UM.Theme.getSize("setting_control").height * 1.2
    property var labelFont: UM.Theme.getFont("default")

    property string machineStackId: Cura.MachineManager.activeMachine.id

    Label {
        id: header
        text: catalog.i18nc("@header", "Generation")
        font: UM.Theme.getFont("medium")
        color: UM.Theme.getColor("small_button_text")
        height: contentHeight
        renderType: Text.NativeRendering

        anchors
        {
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

        Repeater
        {
            id: repeater
            model: extrudersModel
            delegate: UM.TabRowButton
            {
                contentItem: Item
                {
                    Cura.RokitExtruderIcon
                    {
                        anchors.horizontalCenter: parent.horizontalCenter
                        materialColor: model.color
                        width: parent.height
                        height: parent.height
                    }
                }
                onClicked:
                {
                    Cura.ExtruderManager.setActiveExtruderIndex(tabBar.currentIndex)
                }
            }
        }
    }

    function getActiveExtruderId() {
        return extrudersModel.items[tabBar.currentIndex].id
    }

    function getActiveExtruderName() {
        return extrudersModel.items[tabBar.currentIndex].name
    }

    function getExtruderType() {
        var lists = Cura.MachineManager.activeStack.variant.name.split(" ")
        if (lists.length > 0)
            return lists[0]

        return ""
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
            Rectangle
            {
                anchors
                {
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
            property real controlWidth: 
            {
                (paddedWidth - textWidth - UM.Theme.getSize("print_setup_big_item").height * 0.5 - UM.Theme.getSize("default_margin").width) / 3.2
            }

            Row { // Material Configuration Bar
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: Cura.MachineManager.activeMachine.hasMaterials

                RokitMenuBar { name: "Material Configuration - " + Cura.MachineManager.activeStack.variant.name + " " + Cura.MachineManager.activeStack.material.name}
            }

            Row { // Nozzle Guage
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: !Cura.MachineManager.activeMachine.hasMaterials

                RokitLabel { name: (getActiveExtruderName() === "Left") ? Cura.MachineManager.activeDefinitionVariantsName : "Needle Guage" }

                ToolButton
                {
                    text: Cura.MachineManager.activeStack != null ? Cura.MachineManager.activeStack.variant.name : ""
                    width: selectors.controlWidth
                    height: parent.height
                }
            }

            Row { // Material
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: !Cura.MachineManager.activeMachine.hasMaterials

                RokitLabel { name: catalog.i18nc("@label", "Material") }

                ToolButton
                {
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
                anchors
                {
                    //top: dispensor_vac_power.bottom
                    left: selectors.left
                    right: selectors.right
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
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: Cura.MachineManager.activeMachine.hasMaterials

                RokitMenuBar { name: "Layer Quality" }
            }

            GridLayout {
                id: layer

                Layout.fillWidth: true
                columnSpacing: 24 * screenScaleFactor
                rowSpacing: 1 * screenScaleFactor
                anchors
                {
                    //top: dispensor_vac_power.bottom
                    left: selectors.left
                    right: selectors.right
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
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: Cura.MachineManager.activeMachine.hasMaterials

                RokitMenuBar { name: "UV Setting" }
            }

            GridLayout {
                id: uv

                Layout.fillWidth: true
                columnSpacing: 24 * screenScaleFactor
                rowSpacing: 1 * screenScaleFactor
                anchors
                {
                    //top: dispensor_vac_power.bottom
                    left: selectors.left
                    right: selectors.right
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
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: getExtruderType() === "Syringe"

                RokitMenuBar { name: "Dispensor" + " - " + getExtruderType() } 
            }

            Row {
                visible: getExtruderType() === "Syringe"

                GridLayout {
                    id: dispensor

                    Layout.fillWidth: true
                    columnSpacing: 24 * screenScaleFactor
                    rowSpacing: 1 * screenScaleFactor
                    anchors
                    {
                        //top: dispensor_vac_power.bottom
                        left: selectors.left
                        right: selectors.right
                        margins: UM.Theme.getSize("default_margin").width * 2
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
}
