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

            Column
            {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop

                spacing: base.columnSpacing + 5
                
                Label  // "Model"
                {
                    id: model
                    text: catalog.i18nc("@label", "Model: abc.stl")
                    font: base.labelFont
                    color: UM.Theme.getColor("text")
                    renderType: Text.NativeRendering
                    width: base.labelWidth
                }

                Label  // "Material"
                {
                    id: model2
                    text: catalog.i18nc("@label", "Material: ") + machineStackId.properties.value
                    font: base.labelFont
                    width: base.labelWidth
                }

                Label  // "Needle gauge"
                {
                    id: needleGauge
                    text: catalog.i18nc("@label", "Needle gauge: ")
                    font: base.labelFont
                    width: base.labelWidth
                }

                Cura.NumericTextFieldWithUnit  // "Vacuum"
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

                Cura.NumericTextFieldWithUnit  // "Interval"
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

                Cura.NumericTextFieldWithUnit  // "Set.p"
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

                Cura.NumericTextFieldWithUnit  // "Vac.p"
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

                Cura.NumericTextFieldWithUnit  // "Layers"
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

                Cura.NumericTextFieldWithUnit  // "Time"
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

                Cura.NumericTextFieldWithUnit  // "Dimming"
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
