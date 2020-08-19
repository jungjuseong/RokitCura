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

    UM.I18nCatalog
    {
        id: catalog
        name: "cura"
    }
    //property var extrudersModel: Cura.ExtrudersModel {}

    width: parent.width
    height: childrenRect.height

    property int columnWidth: ((parent.width - 2 * UM.Theme.getSize("default_margin").width) / 2) | 0
    
    property int columnSpacing: 4 * screenScaleFactor
    property int propertyStoreIndex: manager ? manager.storeContainerIndex : 1  // definition_changes

    property int labelWidth: (columnWidth * 2 / 3 - UM.Theme.getSize("default_margin").width * 2) | 0
    property int controlWidth: (columnWidth / 3) | 0
    property int controlHeight: UM.Theme.getSize("setting_control").height * 1.2

    property var labelFont: UM.Theme.getFont("default")

    property string machineStackId: Cura.MachineManager.activeMachine.id

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

        GridLayout {
            id: grid

            anchors
            {
                top: grid.top
                left: parent.left
                right: parent.right
                margins: UM.Theme.getSize("default_margin").width
            }

            columns: 3

            Text { text: "Three"; font.bold: true; }
            Text { text: "words"; color: "red" }
            Text { text: "in"; font.underline: true }
        }

        RowLayout
        {
            id: upperBlock
            anchors
            {
                top: grid.top
                left: parent.left
                right: parent.right
                margins: UM.Theme.getSize("default_margin").width
            }
            spacing: UM.Theme.getSize("default_margin").width
            
            // Material
            Column
            {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop

                spacing: base.columnSpacing
                
                Label   // Title Label
                {
                    text: {
                        const guageType = (getActiveExtruderName() === "Left") ? Cura.MachineManager.activeDefinitionVariantsName : "Needle Gauge"
                        return Cura.MachineManager.activeStack.variant.name + " - " + Cura.MachineManager.activeStack.material.name
                    }

                    font: UM.Theme.getFont("medium_bold")
                    color: UM.Theme.getColor("text")
                    renderType: Text.NativeRendering
                    width: parent.width
                    elide: Text.ElideRight
                }

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "material_print_temperature"
                    labelText: catalog.i18nc("@label", "Print Temp.")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    controlHeight: base.controlHeight
                    unitText: catalog.i18nc("@label", "°C")

                    textField.readOnly: true
                }

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "material_bed_temperature"
                    labelText: catalog.i18nc("@label", "Bed Temp.")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    controlHeight: base.controlHeight
                    unitText: catalog.i18nc("@label", "°C")

                    textField.readOnly: true
                }
            }

            // =======================================
            // Layer Quality
            // =======================================
            Column
            {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop

                spacing: base.columnSpacing

                Label   // Title Label
                {
                    text: catalog.i18nc("@title:label", "Layer Quality")
                    font: UM.Theme.getFont("medium_bold")
                    color: UM.Theme.getColor("text")
                    renderType: Text.NativeRendering
                    width: parent.width
                    elide: Text.ElideRight
                }

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "layer_height"
                    labelText: catalog.i18nc("@label", "Layer Height")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    controlHeight: base.controlHeight
                    unitText: catalog.i18nc("@label", "mm")

                    textField.readOnly: true
                }

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "infill_pattern"
                    labelText: catalog.i18nc("@label", "Infill Pattern")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    controlHeight: base.controlHeight

                    textField.readOnly: true
                }

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "infill_sparse_density"
                    labelText: catalog.i18nc("@label", "Infill Density")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    controlHeight: base.controlHeight
                    unitText: catalog.i18nc("@label", "%")

                    textField.readOnly: true
                }
            }
        }

        RowLayout
        {
            id: secondBlock
            anchors
            {
                top: upperBlock.bottom
                left: parent.left
                right: parent.right
                margins: UM.Theme.getSize("default_margin").width
            }
            spacing: UM.Theme.getSize("default_margin").width
            
            // UV
            Column
            {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop

                spacing: base.columnSpacing
                
                Label   // Title Label
                {
                    text: catalog.i18nc("@title:label", "UV")

                    font: UM.Theme.getFont("medium_bold")
                    color: UM.Theme.getColor("text")
                    renderType: Text.NativeRendering
                    width: parent.width
                    elide: Text.ElideRight
                }

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "uv_type"
                    labelText: catalog.i18nc("@label", "Type")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    controlHeight: base.controlHeight
                    unitText: catalog.i18nc("@label", "nm")

                    textField.readOnly: true
                }

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "uv_time"
                    labelText: catalog.i18nc("@label", "Time")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    controlHeight: base.controlHeight
                    unitText: catalog.i18nc("@label", "sec")

                    textField.readOnly: true
                }
                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "uv_dimming"
                    labelText: catalog.i18nc("@label", "Dimming")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    controlHeight: base.controlHeight
                    unitText: catalog.i18nc("@label", "%")

                    textField.readOnly: true
                }

            }

            // =======================================
            // Dispensor
            // =======================================
            Column
            {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop

                spacing: base.columnSpacing

                Label   // Title Label
                {
                    text: catalog.i18nc("@title:label", "Layer Quality")
                    font: UM.Theme.getFont("medium_bold")
                    color: UM.Theme.getColor("text")
                    renderType: Text.NativeRendering
                    width: parent.width
                    elide: Text.ElideRight
                }

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "layer_height"
                    labelText: catalog.i18nc("@label", "Layer Height")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    controlHeight: base.controlHeight
                    unitText: catalog.i18nc("@label", "mm")

                    textField.readOnly: true
                }

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "infill_pattern"
                    labelText: catalog.i18nc("@label", "Infill Pattern")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    controlHeight: base.controlHeight

                    textField.readOnly: true
                }

                Cura.NumericTextFieldWithUnit
                {
                    containerStackId: getActiveExtruderId()
                    settingKey: "infill_sparse_density"
                    labelText: catalog.i18nc("@label", "Infill Density")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    controlHeight: base.controlHeight
                    unitText: catalog.i18nc("@label", "%")

                    textField.readOnly: true
                }
            }
        }
    }
}
