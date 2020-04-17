// Copyright (c) 2019 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.6
import QtQuick.Controls 2.0
import QtQuick.Controls 1.1 as OldControls

import Cura 1.0 as Cura
import UM 1.3 as UM

Item
{
    id: base

    UM.I18nCatalog
    {
        id: catalog
        name: "cura"
    }

    width: parent.width
    height: childrenRect.height

    Label
    {
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

    UM.TabRow
    {
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

    Rectangle
    {
        width: parent.width
        height: childrenRect.height
        anchors.top: tabBar.bottom

        radius: tabBar.visible ? UM.Theme.getSize("default_radius").width : 0
        border.width: tabBar.visible ? UM.Theme.getSize("default_lining").width : 0
        border.color: UM.Theme.getColor("lining")
        color: UM.Theme.getColor("main_background")

        //Remove rounding and lining at the top.
        Rectangle
        {
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

        Column
        {
            id: selectors

            padding: UM.Theme.getSize("default_margin").width
            spacing: UM.Theme.getSize("default_margin").height / 2

            readonly property real paddedWidth: parent.width - padding * 2
            property real textWidth: Math.round(paddedWidth * 0.3)
            property real controlWidth: 
            {
                (paddedWidth - textWidth - UM.Theme.getSize("print_setup_big_item").height * 0.5 - UM.Theme.getSize("default_margin").width) / 2
            }
            
            
            Row // Material Configuration Bar
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: Cura.MachineManager.activeMachine.hasMaterials

                RokitMenuBar { name: "Material Configuration" }
            }

            Row 
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: Cura.MachineManager.activeMachine.hasMaterials

                RokitLabel
                {
                    name: catalog.i18nc("@label", "Material")
                }

                ToolButton
                {
                    text: Cura.MachineManager.activeStack !== null ? Cura.MachineManager.activeStack.material.name : ""
                    width: selectors.controlWidth
                    height: parent.height
                }
            }

            Row // Nozzle
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: Cura.MachineManager.activeMachine.hasMaterials

                RokitLabel
                {
                    name: (getActiveExtruderName() === "Left") ? Cura.MachineManager.activeDefinitionVariantsName : "Needle Guage"
                }

                ToolButton
                {
                    text: Cura.MachineManager.activeStack != null ? Cura.MachineManager.activeStack.variant.name : ""
                    width: selectors.controlWidth
                    height: parent.height
                }
            }

            Row // print temperature
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: Cura.MachineManager.activeMachine.hasMaterials

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "material_print_temperature"
                    labelText: catalog.i18nc("@label", "Print Temperature")
                    labelFont: UM.Theme.getFont("default")
                    labelWidth: selectors.textWidth - 8
                    controlWidth: selectors.controlWidth
                    controlHeight: parent.height
                    unitText: catalog.i18nc("@label", "°C")

                    textField.readOnly: true
                    textField.horizontalAlignment: TextInput.AlignHCenter
                }
            }
            
            Row // bed temperature
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: Cura.MachineManager.activeMachine.hasMaterials

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "material_bed_temperature"
                    labelText: catalog.i18nc("@label", "Bed Temperature")
                    labelFont: UM.Theme.getFont("default")
                    labelWidth: selectors.textWidth - 8
                    controlWidth: selectors.controlWidth
                    controlHeight: parent.height
                    unitText: catalog.i18nc("@label", "°C")

                    textField.readOnly: true
                    textField.horizontalAlignment: TextInput.AlignHCenter
                }
            }

            Row // Layer Quality
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: Cura.MachineManager.activeMachine.hasMaterials

                RokitMenuBar { name: "Layer Quality" }
            }

            Row // layer height
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: Cura.MachineManager.activeMachine.hasMaterials

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "layer_height"
                    labelText: catalog.i18nc("@label", "Layer Height")
                    labelFont: UM.Theme.getFont("default")
                    labelWidth: selectors.textWidth - 8
                    controlWidth: selectors.controlWidth
                    controlHeight: parent.height
                    unitText: catalog.i18nc("@label", "mm")

                    textField.readOnly: true
                    textField.horizontalAlignment: TextInput.AlignHCenter
                }
            }
            Row // infill pattern
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: Cura.MachineManager.activeMachine.hasMaterials

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "infill_pattern"
                    labelText: catalog.i18nc("@label", "Infill Pattern")
                    labelFont: UM.Theme.getFont("default")
                    labelWidth: selectors.textWidth - 8
                    controlWidth: selectors.controlWidth
                    controlHeight: parent.height

                    textField.readOnly: true
                    textField.horizontalAlignment: TextInput.AlignHCenter
                }
            }

            Row // UV
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: Cura.MachineManager.activeMachine.hasMaterials

                RokitMenuBar { name: "UV Setting" }
            }

            Row // Layers
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: extrudersModel.items[tabBar.currentIndex].id != ""

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "uv_per_layers"
                    labelText: catalog.i18nc("@label", "UV per Layers")
                    labelFont: UM.Theme.getFont("default")
                    labelWidth: selectors.textWidth - 8
                    controlWidth: selectors.controlWidth
                    controlHeight: parent.height
                    unitText: catalog.i18nc("@label", "layers")

                    textField.readOnly: true
                    textField.horizontalAlignment: TextInput.AlignHCenter
                }
            }

            Row // uv_type
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: extrudersModel.items[tabBar.currentIndex].id != ""

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "uv_type"
                    labelText: catalog.i18nc("@label", "UV type")
                    labelFont: UM.Theme.getFont("default")
                    labelWidth: selectors.textWidth - 8
                    controlWidth: selectors.controlWidth
                    controlHeight: parent.height
                    unitText: catalog.i18nc("@label", "nm")

                    textField.readOnly: true
                    textField.horizontalAlignment: TextInput.AlignHCenter
                }
            }

            Row // uv_time
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: extrudersModel.items[tabBar.currentIndex].id != ""

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "uv_time"
                    labelText: catalog.i18nc("@label", "UV time")
                    labelFont: UM.Theme.getFont("default")
                    labelWidth: selectors.textWidth - 8
                    controlWidth: selectors.controlWidth
                    controlHeight: parent.height
                    unitText: catalog.i18nc("@label", "sec")

                    textField.readOnly: true
                    textField.horizontalAlignment: TextInput.AlignHCenter
                }
            }

            Row // uv_dimming
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: extrudersModel.items[tabBar.currentIndex].id != ""

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "uv_dimming"
                    labelText: catalog.i18nc("@label", "Dimming")
                    labelFont: UM.Theme.getFont("default")
                    labelWidth: selectors.textWidth - 8
                    controlWidth: selectors.controlWidth
                    controlHeight: parent.height
                    unitText: catalog.i18nc("@label", "%")

                    textField.readOnly: true
                    textField.horizontalAlignment: TextInput.AlignHCenter
                }
            }

            Row // Dispensor
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: getExtruderType() === "Syringe"

                RokitMenuBar { name: "Dispensor" + " - " + getExtruderType() } 
            }
            Row // Dispensor shot
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: getExtruderType() === "Syringe"

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "dispensor_shot"
                    labelText: catalog.i18nc("@label", "SHOT")
                    labelFont: UM.Theme.getFont("default")
                    labelWidth: selectors.textWidth - 8
                    controlWidth: selectors.controlWidth
                    controlHeight: parent.height
                    unitText: catalog.i18nc("@label", "sec")

                    textField.readOnly: true
                    textField.horizontalAlignment: TextInput.AlignHCenter
                }
            }
            Row // Dispensor vac
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: getExtruderType() === "Syringe"

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "dispensor_vac"
                    labelText: catalog.i18nc("@label", "VAC")
                    labelFont: UM.Theme.getFont("default")
                    labelWidth: selectors.textWidth - 8
                    controlWidth: selectors.controlWidth
                    controlHeight: parent.height
                    unitText: catalog.i18nc("@label", "sec")

                    textField.readOnly: true
                    textField.horizontalAlignment: TextInput.AlignHCenter
                }
            }

            Row // Dispensor int
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: getExtruderType() === "Syringe"

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "dispensor_int"
                    labelText: catalog.i18nc("@label", "INT")
                    labelFont: UM.Theme.getFont("default")
                    labelWidth: selectors.textWidth - 8
                    controlWidth: selectors.controlWidth
                    controlHeight: parent.height
                    unitText: catalog.i18nc("@label", "kpa")

                    textField.readOnly: true
                    textField.horizontalAlignment: TextInput.AlignHCenter
                }
            }

            Row // Dispensor shot power
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: getExtruderType() === "Syringe"

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "dispensor_shot_power"
                    labelText: catalog.i18nc("@label", "SHOT Power")
                    labelFont: UM.Theme.getFont("default")
                    labelWidth: selectors.textWidth - 8
                    controlWidth: selectors.controlWidth
                    controlHeight: parent.height
                    unitText: catalog.i18nc("@label", "kpa")

                    textField.readOnly: true
                    textField.horizontalAlignment: TextInput.AlignHCenter
                }
            }

            Row // Dispensor vac power
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: getExtruderType() === "Syringe"

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "dispensor_vac_power"
                    labelText: catalog.i18nc("@label", "VAC Power")
                    labelFont: UM.Theme.getFont("default")
                    labelWidth: selectors.textWidth - 8
                    controlWidth: selectors.controlWidth
                    controlHeight: parent.height
                    unitText: catalog.i18nc("@label", "kpa")

                    textField.readOnly: true
                    textField.horizontalAlignment: TextInput.AlignHCenter
                }
            }
        }
    }
}
