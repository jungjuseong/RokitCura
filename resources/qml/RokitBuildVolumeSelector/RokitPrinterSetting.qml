// Copyright (c) 2019 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.3

import UM 1.3 as UM
import Cura 1.1 as Cura

//
// This the content in the "Printer" tab in the Machine Settings dialog.
//
Item
{
    id: base
    UM.I18nCatalog { id: catalog; name: "cura" }

    property int columnWidth: ((parent.width - 2 * UM.Theme.getSize("default_margin").width) / 2) | 0
    property int columnSpacing: 3 * screenScaleFactor
    property int propertyStoreIndex: manager ? manager.storeContainerIndex : 1  // definition_changes

    property int labelWidth: (columnWidth * 2 / 3 - UM.Theme.getSize("default_margin").width * 2) | 0
    property int controlWidth: (columnWidth / 3) | 0
    property var labelFont: UM.Theme.getFont("default")

    property string machineStackId: Cura.MachineManager.activeMachine.id

    property var forceUpdateFunction: manager.forceUpdate

    Cura.RoundedRectangle
    {
        height: 300
        anchors
        {
            top: parent.bottom + 100 // tabBar.bottom
            topMargin: -UM.Theme.getSize("default_lining").height
            bottom: parent.bottom + 400
            left: parent.left
            right: parent.right
        }
        cornerSide: Cura.RoundedRectangle.Direction.Down
        border.color: UM.Theme.getColor("lining")
        border.width: UM.Theme.getSize("default_lining").width
        radius: UM.Theme.getSize("default_radius").width
        color: UM.Theme.getColor("main_background")

        RowLayout
        {
            id: upperBlock
            anchors
            {
                top: parent.top
                left: parent.left
                right: parent.right
                margins: UM.Theme.getSize("default_margin").width
            }
            spacing: UM.Theme.getSize("default_margin").width
            
            // =======================================
            // "Printer Settings"
            // =======================================
            Column
            {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop

                spacing: base.columnSpacing

                Label   // Title Label
                {
                    text: catalog.i18nc("@title:label", "Printer Settings")
                    font: UM.Theme.getFont("medium_bold")
                    color: UM.Theme.getColor("text")
                    renderType: Text.NativeRendering
                    width: parent.width
                    elide: Text.ElideRight
                }

                Cura.NumericTextFieldWithUnit  // "X (Width)"
                {
                    id: machineXWidthField
                    containerStackId: machineStackId
                    settingKey: "machine_width"
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "X (Width)")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    unitText: catalog.i18nc("@label", "mm")
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }

                Cura.NumericTextFieldWithUnit  // "Y (Depth)"
                {
                    id: machineYDepthField
                    containerStackId: machineStackId
                    settingKey: "machine_depth"
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "Y (Depth)")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    unitText: catalog.i18nc("@label", "mm")
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }

                Cura.NumericTextFieldWithUnit  // "Z (Height)"
                {
                    id: machineZHeightField
                    containerStackId: machineStackId
                    settingKey: "machine_height"
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "Z (Height)")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    unitText: catalog.i18nc("@label", "mm")
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }

                Cura.ComboBoxWithOptions  // "Build plate shape"
                {
                    id: buildPlateShapeComboBox
                    containerStackId: machineStackId
                    settingKey: "machine_shape"
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "Build plate shape")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }

                Cura.SimpleCheckBox  // "Origin at center"
                {
                    id: originAtCenterCheckBox
                    containerStackId: machineStackId
                    settingKey: "machine_center_is_zero"
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "Origin at center")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }
            }

        }
    }
}
