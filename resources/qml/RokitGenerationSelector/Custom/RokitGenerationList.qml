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

    Cura.ObjectsModel { id: objectsModel }
    
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

                Rectangle{
                    width:  UM.Theme.getSize("rokit_big_item").width
                    height: UM.Theme.getSize("rokit_big_item").height
                    border.color: UM.Theme.getColor("setting_control_border")
                    radius: UM.Theme.getSize("rokit_combobox_radius").height 
                    color: UM.Theme.getColor("secondary")

                    Text{
                        anchors{
                            verticalCenter: parent.verticalCenter
                            left: parent.left
                            leftMargin: UM.Theme.getSize("default_margin").width 
                        }
                        text: "Material"
                    }
                }
                
                Label  // "Model"
                {
                    id: model
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    text: catalog.i18nc("@label", "Model: "+ objectsModel.name)
                    font: base.labelFont
                    color: UM.Theme.getColor("text")
                    renderType: Text.NativeRendering
                    width: base.labelWidth
                }

                Label  // "Material"
                {
                    id: materialLabel
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    text: catalog.i18nc("@label", "Material: "+ Cura.MachineManager.activeStack.material.name)
                    font: base.labelFont
                    width: base.labelWidth
                }

                Label  // "Needle gauge"
                {
                    id: needleGaugeLabel
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    text: catalog.i18nc("@label", "Needle gauge: " + Cura.MachineManager.activeStack.variant.name)
                    font: base.labelFont
                    width: base.labelWidth
                }

                Rectangle{
                    width:  UM.Theme.getSize("rokit_big_item").width
                    height: UM.Theme.getSize("rokit_big_item").height
                    border.color: UM.Theme.getColor("setting_control_border")
                    radius: UM.Theme.getSize("rokit_combobox_radius").height 
                    color: UM.Theme.getColor("secondary")

                    Text{
                        anchors{
                            verticalCenter: parent.verticalCenter
                            left: parent.left
                            leftMargin: UM.Theme.getSize("default_margin").width 
                        }
                        text: "Print Settings"
                    }
                } 

                Label  // "Layer Height"
                {
                    id: layerHeightLabel
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    text: catalog.i18nc("@label", "Layer height: " + layerHeight.properties.value + "mm")
                    font: base.labelFont
                    width: base.labelWidth
                }

                Label  // "Infill Pattern"
                {
                    id: infillPatternLabel
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    text: catalog.i18nc("@label", "Infill Pattern: " + infillPattern.properties.value)
                    font: base.labelFont
                    width: base.labelWidth
                }

                Cura.RokitSimpleCheckBox  // "Support"
                {
                    id: generationSupportcheck
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    containerStackId: machineStackId
                    settingKey: "support_enable"
                    
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "Support")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth *1.7
                    forceUpdateOnChangeFunction: forceUpdateFunction
                }

                Label  // "Adhesion type"
                {
                    id: adhesionTypeLabel
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    text: catalog.i18nc("@label", "Adhesion Type: " + adhesionType.properties.value)
                    font: base.labelFont
                    width: base.labelWidth
                }

                // Cura.RokitSimpleCheckBox  // "Adhesion"
                // {
                //     id: generationAdhesioncheck
                //     containerStackId: machineStackId
                //     settingKey: "adhesion_type"
                    
                //     settingStoreIndex: propertyStoreIndex
                //     labelText: catalog.i18nc("@label", "Adhesion")
                //     labelFont: base.labelFont
                //     labelWidth: base.labelWidth *1.8
                //     forceUpdateOnChangeFunction: forceUpdateFunction
                // }

                // Dispensor
                Rectangle{
                    width:  UM.Theme.getSize("rokit_big_item").width
                    height: UM.Theme.getSize("rokit_big_item").height
                    border.color: UM.Theme.getColor("setting_control_border")
                    radius: UM.Theme.getSize("rokit_combobox_radius").height 
                    color: UM.Theme.getColor("secondary")

                    Text{
                        anchors{
                            verticalCenter: parent.verticalCenter
                            left: parent.left
                            leftMargin: UM.Theme.getSize("default_margin").width
                        }
                        text: "Dispensor"
                    }
                }

                Row{
                    spacing: UM.Theme.getSize("default_margin")
                    
                    Cura.RokitTextFieldWithUnit  // "Vacuum"
                    {
                        id: generationVacuumcheck
                        containerStackId: machineStackId
                        settingKey: "dispensor_vac"   //--
                        settingStoreIndex: propertyStoreIndex
                        labelText: catalog.i18nc("@label", "Vac")
                        labelFont: base.labelFont
                        labelWidth: base.labelWidth/6.4
                        controlWidth: base.controlWidth/2.5
                        unitText: catalog.i18nc("@label", "sec")
                        forceUpdateOnChangeFunction: forceUpdateFunction
                    }

                    Rectangle{
                        width:  UM.Theme.getSize("default_margin").width
                        height: parent.height
                    }

                    Cura.RokitTextFieldWithUnit  // "Interval"
                    {
                        id: generationIntervalcheck
                        containerStackId: machineStackId
                        settingKey: "dispensor_int"   //--
                        settingStoreIndex: propertyStoreIndex
                        labelText: catalog.i18nc("@label", "Int")
                        labelFont: base.labelFont
                        labelWidth: base.labelWidth/6.8
                        controlWidth: base.controlWidth/2.5
                        unitText: catalog.i18nc("@label", "kpa")
                        forceUpdateOnChangeFunction: forceUpdateFunction
                    }

                    Rectangle{
                        width:  UM.Theme.getSize("default_margin").width
                        height: parent.height
                    }


                    Cura.RokitTextFieldWithUnit  // "Set.p"
                    {
                        id: generationSetPcheck
                        containerStackId: machineStackId
                        settingKey: "dispensor_shot_power"   //--
                        settingStoreIndex: propertyStoreIndex
                        labelText: catalog.i18nc("@label", "Set.p")
                        labelFont: base.labelFont
                        labelWidth: base.labelWidth/4.7
                        controlWidth: base.controlWidth/2.5
                        unitText: catalog.i18nc("@label", "kpa")
                        forceUpdateOnChangeFunction: forceUpdateFunction
                    }

                    Rectangle{
                        width:  UM.Theme.getSize("default_margin").width
                        height: parent.height
                    }


                    Cura.RokitTextFieldWithUnit  // "Vac.p"
                    {
                        id: generationVacPcheck
                        containerStackId: machineStackId
                        settingKey: "dispensor_vac_power"   //--
                        settingStoreIndex: propertyStoreIndex
                        labelText: catalog.i18nc("@label", "Vac.p")
                        labelFont: base.labelFont
                        labelWidth: base.labelWidth/4.7
                        controlWidth: base.controlWidth/2.5
                        unitText: catalog.i18nc("@label", "kpa")
                        forceUpdateOnChangeFunction: forceUpdateFunction
                    }
                }

                Rectangle{
                    width:  UM.Theme.getSize("rokit_big_item").width
                    height: UM.Theme.getSize("rokit_big_item").height
                    border.color: UM.Theme.getColor("setting_control_border")
                    radius: UM.Theme.getSize("rokit_combobox_radius").height 
                    color: UM.Theme.getColor("secondary")

                    Text{
                        anchors{
                            verticalCenter: parent.verticalCenter
                            left: parent.left
                            leftMargin: UM.Theme.getSize("default_margin").width 
                        }
                        text: "UV"
                    }
                }
                
                // UV
                Row{
                    //spacing: UM.Theme.getSize("narrow_margin")

                    Cura.RokitTextFieldWithUnit  // "Layers"
                    {
                        id: generationLayerscheck
                        containerStackId: machineStackId
                        settingKey: "uv_per_layers"   //--
                        settingStoreIndex: propertyStoreIndex
                        labelText: catalog.i18nc("@label", "Layers")
                        labelFont: base.labelFont
                        labelWidth: base.labelWidth / 3.5
                        controlWidth: base.controlWidth/2.1
                        forceUpdateOnChangeFunction: forceUpdateFunction
                    }

                    Rectangle{
                        width:  UM.Theme.getSize("default_margin").width
                        height: parent.height
                    }

                    Cura.RokitTextFieldWithUnit  // "Time"
                    {
                        id: generationTimecheck
                        containerStackId: machineStackId
                        settingKey: "uv_time"   //--
                        settingStoreIndex: propertyStoreIndex
                        labelText: catalog.i18nc("@label", "Time")
                        labelFont: base.labelFont
                        labelWidth: base.labelWidth / 4.2
                        controlWidth: base.controlWidth/2.1
                        unitText: catalog.i18nc("@label", "sec")
                        forceUpdateOnChangeFunction: forceUpdateFunction
                    }

                    Rectangle{
                        width:  UM.Theme.getSize("default_margin").width
                        height: parent.height
                    }

                    Cura.RokitTextFieldWithUnit  // "Dimming"
                    {
                        id: generationDimmingcheck
                        containerStackId: machineStackId
                        settingKey: "uv_dimming"   //--
                        settingStoreIndex: propertyStoreIndex
                        labelText: catalog.i18nc("@label", "Dimming")
                        labelFont: base.labelFont
                        labelWidth: base.labelWidth / 2.7
                        controlWidth: base.controlWidth /2.1
                        unitText: catalog.i18nc("@label", "%")
                        forceUpdateOnChangeFunction: forceUpdateFunction
                    }
                }

            }
        }
    }

    // Left Extruder Type
    UM.SettingPropertyProvider
    {
        id: leftExtruderType
        containerStack: Cura.MachineManager.activeMachine
        key: "left_extruder_type" //     key: "machine_nozzle_size"
        watchedProperties: [ "value" ]
        storeIndex: propertyStoreIndex
    }

    // Layer height
    UM.SettingPropertyProvider
    {
        id: layerHeight
        containerStack: Cura.MachineManager.activeMachine
        key: "layer_height"
        watchedProperties: [ "value" ]
        storeIndex: propertyStoreIndex
    }

    // Infill pattern
    UM.SettingPropertyProvider
    {
        id: infillPattern
        containerStack: Cura.MachineManager.activeMachine
        key: "infill_pattern"
        watchedProperties: [ "value" ]
        storeIndex: propertyStoreIndex
    }

    // Adhesion pattern
    UM.SettingPropertyProvider
    {
        id: adhesionType
        containerStack: Cura.MachineManager.activeMachine
        key: "adhesion_type"
        watchedProperties: [ "value" ]
        storeIndex: propertyStoreIndex
    }
}
