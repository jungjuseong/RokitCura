// Copyright (c) 2019 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.3

import UM 1.3 as UM
import Cura 1.1 as Cura

Item
{
    id: base
    UM.I18nCatalog { id: catalog; name: "cura" }

    property int columnWidth: 150 * 2 - 2 * UM.Theme.getSize("default_margin").width
    property int columnSpacing: 3 * screenScaleFactor
    property int propertyStoreIndex: manager ? manager.storeContainerIndex : 1  // definition_changes

    property int labelWidth: columnWidth * 0.6 - UM.Theme.getSize("default_margin").width
    property int controlWidth: columnWidth * 0.4
    property var labelFont: UM.Theme.getFont("default")

    property string machineStackId: Cura.MachineManager.activeMachine.id
    property var forceUpdateFunction: manager.forceUpdate
    
    Cura.RoundedRectangle
    {
        cornerSide: Cura.RoundedRectangle.Direction.Down
        border.color: UM.Theme.getColor("lining")
        border.width: UM.Theme.getSize("default_lining").width
        radius: UM.Theme.getSize("default_radius").width
        color: UM.Theme.getColor("main_background")
        height: upperBlock.height + 20 
        //width: 300

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
            // "Build Plate Settings"
            // =======================================
            Column
            {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop

                spacing: base.columnSpacing + 5

                Label   // Title Label
                {
                    text: catalog.i18nc("@title:label", "Build Volume Settings")
                    font: UM.Theme.getFont("medium_bold")
                    color: UM.Theme.getColor("text")
                    renderType: Text.NativeRendering
                    width: parent.width
                    elide: Text.ElideRight
                }

                Cura.NumericTextFieldWithUnit  // "X (Width)" -> "File"
                {
                    id: generationFilecheck
                    containerStackId: machineStackId
                    settingKey: "machine_width"
                    settingStoreIndex: propertyStoreIndex
                    //labelText: catalog.i18nc("@label", "X (Width)")
                    labelText: catalog.i18nc("@label", "File")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    //unitText: catalog.i18nc("@label", "mm")
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }

                // Rectangle
                // {
                //     id: a
                //     width: parent.width
                //     height: UM.Theme.getSize("default_lining").height
                //     color: UM.Theme.getColor("lining")
                // }

                Cura.NumericTextFieldWithUnit  // "Y (Depth)" -> "Material"
                {
                    id: generationMaterialcheck
                    containerStackId: machineStackId
                    settingKey: "machine_depth"
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "Material")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }

                Cura.NumericTextFieldWithUnit  // "Z (Height)" -> "Needle gauge"
                {
                    id: generationNeedleGaugecheck
                    containerStackId: machineStackId
                    settingKey: "machine_nozzle_id"
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "Needle gauge")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }

                Cura.NumericTextFieldWithUnit  // "Z (Height)" -> "Needle Temperature"
                {
                    id: generationNeedleTemperaturecheck
                    containerStackId: machineStackId
                    settingKey: "default_material_print_temperature"
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "Needle Temperature")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    unitText: catalog.i18nc("@label", "°C")
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }

                Cura.NumericTextFieldWithUnit  // "Z (Height)" -> "Layer height"
                {
                    id: generationLayerHeightcheck
                    containerStackId: machineStackId
                    settingKey: "layer_height"
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "Layer height")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    unitText: catalog.i18nc("@label", "mm")
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }

                Cura.NumericTextFieldWithUnit  // "Z (Height)" -> "infill"
                {
                    id: generationInfillcheck
                    containerStackId: machineStackId
                    settingKey: "infill_pattern"   //--
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "Infill Pattern")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }

                // Cura.ComboBoxWithOptions  // "Build plate shape" // 콤보박스
                // {
                //     id: buildPlateShapeComboBox
                //     containerStackId: machineStackId
                //     settingKey: "machine_shape"
                //     settingStoreIndex: propertyStoreIndex
                //     labelText: catalog.i18nc("@label", "Build plate shape")
                //     labelFont: base.labelFont
                //     labelWidth: base.labelWidth
                //     controlWidth: base.controlWidth
                //     forceUpdateOnChangeFunction: forceUpdateFunction
                // }

                Cura.SimpleCheckBox  // "Origin at center" -> "Support"
                {
                    id: generationSupportcheck
                    containerStackId: machineStackId
                    settingKey: "support_enable"
                    
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "Support")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }

                Cura.SimpleCheckBox  // "Origin at center" -> "Adhesion"
                {
                    id: generationAdhesioncheck
                    containerStackId: machineStackId
                    settingKey: "support_enable"
                    
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "Adhesion")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }

                // Rectangle
                // {
                //     width: parent.width
                //     height: UM.Theme.getSize("default_lining").height
                //     color: UM.Theme.getColor("lining")
                // }

                Cura.NumericTextFieldWithUnit  // "Z (Height)" -> "Vacuum"
                {
                    id: generationVacuumcheck
                    containerStackId: machineStackId
                    settingKey: "dispensor_vac"   //--
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "Vac")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }

                Cura.NumericTextFieldWithUnit  // "Z (Height)" -> "Interval"
                {
                    id: generationIntervalcheck
                    containerStackId: machineStackId
                    settingKey: "dispensor_int"   //--
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "Int")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }

                Cura.NumericTextFieldWithUnit  // "Z (Height)" -> "Set.p"
                {
                    id: generationSetPcheck
                    containerStackId: machineStackId
                    settingKey: "dispensor_shot_power"   //--
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "Set.p")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }

                Cura.NumericTextFieldWithUnit  // "Z (Height)" -> "Vac.p"
                {
                    id: generationVacPcheck
                    containerStackId: machineStackId
                    settingKey: "dispensor_vac_power"   //--
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "Vac.p")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }

                // Rectangle
                // {
                //     width: parent.width
                //     height: UM.Theme.getSize("default_lining").height
                //     color: UM.Theme.getColor("lining")
                // }

                Cura.NumericTextFieldWithUnit  // "Z (Height)" -> "Layers"
                {
                    id: generationLayerscheck
                    containerStackId: machineStackId
                    settingKey: "uv_per_layers"   //--
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "Layers")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }

                // Cura.NumericTextFieldWithUnit  // "Z (Height)" -> "Power"
                // {
                //     id: generationPowercheck
                //     containerStackId: machineStackId
                //     settingKey: "infill_pattern"   //--
                //     settingStoreIndex: propertyStoreIndex
                //     labelText: catalog.i18nc("@label", "Power")
                //     labelFont: base.labelFont
                //     labelWidth: base.labelWidth
                //     controlWidth: base.controlWidth
                //     forceUpdateOnChangeFunction: forceUpdateFunction
                // }

                Cura.NumericTextFieldWithUnit  // "Z (Height)" -> "Time"
                {
                    id: generationTimecheck
                    containerStackId: machineStackId
                    settingKey: "uv_time"   //--
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "Time")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }

                Cura.NumericTextFieldWithUnit  // "Z (Height)" -> "Dimming"
                {
                    id: generationDimmingcheck
                    containerStackId: machineStackId
                    settingKey: "uv_dimming"   //--
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "Dimming")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth
                    controlWidth: base.controlWidth
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }
            }
        }
    }
}
