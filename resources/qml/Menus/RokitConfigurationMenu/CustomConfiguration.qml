// Copyright (c) 2019 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.6
import QtQuick.Controls 2.0
import QtQuick.Controls 1.1 as OldControls

import Cura 1.0 as Cura
import UM 1.3 as UM

import "Custom"

// Nozzle Temperature Make
//  Bed Temperature Make
// Left::Syringe selector

Item
{

    id: base

    property string machineStackId: Cura.MachineManager.activeMachine.id
    property var forceUpdateFunction: manager.forceUpdate
    property int propertyStoreIndex: manager ? manager.storeContainerIndex : 1  // definition_changes

    property int columnWidth: ((parent.width - 2 * UM.Theme.getSize("default_margin").width) / 2) | 0
    property int columnSpacing: 3 * screenScaleFactor
    property int labelWidth: (columnWidth * 2 / 3 - UM.Theme.getSize("default_margin").width * 2) | 0
    property int controlWidth: (columnWidth / 3) | 0
    property var labelFont: UM.Theme.getFont("default")
    
    property bool leftSyringe: null


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
        text: catalog.i18nc("@header", "Material Configuration")
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
                    Cura.ExtruderIcon
                    {
                        anchors.horizontalCenter: parent.horizontalCenter
                        materialColor: model.color
                        extruderEnabled: model.enabled
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

        //When active extruder changes for some other reason, switch tabs.
        //Don't directly link currentIndex to Cura.ExtruderManager.activeExtruderIndex!
        //This causes a segfault in Qt 5.11. Something with VisualItemModel removing index -1. We have to use setCurrentIndex instead.
        Connections
        {
            target: Cura.ExtruderManager
            onActiveExtruderChanged:
            {
                tabBar.setCurrentIndex(Cura.ExtruderManager.activeExtruderIndex);
            }
        }

        // Can't use 'item: ...activeExtruderIndex' directly apparently, see also the comment on the previous block.
        onVisibleChanged:
        {
            if (tabBar.visible)
            {
                tabBar.setCurrentIndex(Cura.ExtruderManager.activeExtruderIndex);
            }
        }

        //When the model of the extruders is rebuilt, the list of extruders is briefly emptied and rebuilt.
        //This causes the currentIndex of the tab to be in an invalid position which resets it to 0.
        //Therefore we need to change it back to what it was: The active extruder index.
        Connections
        {
            target: repeater.model
            onModelChanged:
            {
                tabBar.setCurrentIndex(Cura.ExtruderManager.activeExtruderIndex)
            }
        }
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
            spacing: UM.Theme.getSize("default_margin").height

            property var model: extrudersModel.items[tabBar.currentIndex]

            readonly property real paddedWidth: parent.width - padding * 2
            property real textWidth: Math.round(paddedWidth * 0.3)
            property real controlWidth:
            {
                if(instructionLink == "")
                {
                    return paddedWidth - textWidth
                }
                else
                {
                    return paddedWidth - textWidth - UM.Theme.getSize("print_setup_big_item").height * 0.5 - UM.Theme.getSize("default_margin").width
                }
            }
            property string instructionLink: Cura.MachineManager.activeStack != null ? Cura.ContainerManager.getContainerMetaDataEntry(Cura.MachineManager.activeStack.material.id, "instruction_link", ""): ""

            Row  // enable
            {
                height: visible ? UM.Theme.getSize("setting_control").height : 0
                visible: false // extrudersModel.count > 1  // If there is only one extruder, there is no point to enable/disable that.

                Label
                {
                    text: catalog.i18nc("@label", "Enabled")
                    verticalAlignment: Text.AlignVCenter
                    font: UM.Theme.getFont("default")
                    color: UM.Theme.getColor("text")
                    height: parent.height
                    width: selectors.textWidth
                    renderType: Text.NativeRendering
                }

                OldControls.CheckBox
                {
                    id: enabledCheckbox
                    checked: Cura.MachineManager.activeStack != null ? Cura.MachineManager.activeStack.isEnabled : false
                    enabled: !checked || Cura.MachineManager.numberExtrudersEnabled > 1 //Disable if it's the last enabled extruder.
                    height: parent.height
                    style: UM.Theme.styles.checkbox

                    /* Use a MouseArea to process the click on this checkbox.
                       This is necessary because actually clicking the checkbox
                       causes the "checked" property to be overwritten. After
                       it's been overwritten, the original link that made it
                       depend on the active extruder stack is broken. */
                    MouseArea
                    {
                        anchors.fill: parent
                        onClicked: Cura.MachineManager.setExtruderEnabled(Cura.ExtruderManager.activeExtruderIndex, !parent.checked)
                        enabled: parent.enabled
                    }
                }
            }

            Row  // Extuder Type
            {
                id: extruderTypeItem
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: tabBar.currentIndex == 0? true: false && Cura.MachineManager.activeMachine.hasMaterials
                enabled: tabBar.currentIndex == 0? true: false && Cura.MachineManager.activeMachine.hasMaterials
                
                Label
                {
                    text: catalog.i18nc("@label", "Extruder Type")
                    verticalAlignment: Text.AlignVCenter
                    font: UM.Theme.getFont("default")
                    color: UM.Theme.getColor("text")
                    height: parent.height
                    width: selectors.textWidth
                    renderType: Text.NativeRendering
                }

                Cura.ComboBox{
                    id: comboBox
                    visible: True

                    width: selectors.controlWidth
                    height: parent.height
                    textRole: "name"

                    baselineOffset: null

                    model: ListModel{
                        id: leftExtruderModel

                        ListElement{name: "FFF Extruder"; index: 0}
                        ListElement{name: "Hot melt"; index: 1}
                        ListElement{name: "Syringe"; index: 2}
                    }

                    // currentIndex:
                    // {
                    //     var currentValue = propertyProvider.properties.value
                    //     var index = 0
                    //     for (var i = 0; i < model.count; i++)
                    //     {
                    //         if (model.get(i).value == currentValue)
                    //         {
                    //             index = i
                    //             break
                    //         }
                    //     }
                    //     return index
                    // }

                    onActivated:
                    {
                        var newValue = model.get(index).name
                        if(newValue=="Syringe")
                            leftSyringe = true
                        else
                            leftSyringe = false

                        leftExtruderType.setPropertyValue("value", newValue)
                        
                        // if (propertyProvider.properties.value != newValue)
                        // {
                        //     if (setValueFunction !== null)
                        //     {
                        //         setValueFunction(newValue)
                        //     }
                        //     else
                        //     {
                        //         propertyProvider.setPropertyValue("value", newValue)
                        //     }
                        //     forceUpdateOnChangeFunction()
                        //     afterOnEditingFinishedFunction()
                        // }
                    }
                }
            }

            Row  // Material
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: Cura.MachineManager.activeMachine.hasMaterials

                Label
                {
                    text: catalog.i18nc("@label", "Material")
                    verticalAlignment: Text.AlignVCenter
                    font: UM.Theme.getFont("default")
                    color: UM.Theme.getColor("text")
                    height: parent.height
                    width: selectors.textWidth
                    renderType: Text.NativeRendering
                }

                OldControls.ToolButton
                {
                    id: materialSelection

                    property bool valueError: Cura.MachineManager.activeStack !== null ? Cura.ContainerManager.getContainerMetaDataEntry(Cura.MachineManager.activeStack.material.id, "compatible", "") !== "True" : true
                    property bool valueWarning: !Cura.MachineManager.isActiveQualitySupported

                    text: Cura.MachineManager.activeStack !== null ? Cura.MachineManager.activeStack.material.name : ""
                    tooltip: text
                    enabled: enabledCheckbox.checked

                    width: selectors.controlWidth
                    height: parent.height

                    style: UM.Theme.styles.print_setup_header_button
                    activeFocusOnPress: true
                    menu: Cura.MaterialMenu
                    {
                        extruderIndex: Cura.ExtruderManager.activeExtruderIndex
                        updateModels: materialSelection.visible
                    }
                }
                Item
                {
                    width: instructionButton.width + 2 * UM.Theme.getSize("default_margin").width
                    height: instructionButton.visible ? materialSelection.height: 0
                    Button
                    {
                        id: instructionButton
                        hoverEnabled: true
                        contentItem: Item {}
                        height: 0.5 * materialSelection.height
                        width: height
                        anchors.centerIn: parent
                        background: UM.RecolorImage
                        {
                            source: UM.Theme.getIcon("printing_guideline")
                            color: instructionButton.hovered ? UM.Theme.getColor("primary") : UM.Theme.getColor("icon")
                        }
                        visible: selectors.instructionLink != ""
                        onClicked:Qt.openUrlExternally(selectors.instructionLink)
                    }
                }
            }

            Row // Nozzle gauage
            {
                height: visible ? UM.Theme.getSize("print_setup_big_item").height : 0
                visible: Cura.MachineManager.activeMachine.hasVariants

                Label
                {
                    //text: Cura.MachineManager.activeDefinitionVariantsName
                    // Left 이면서 주사기(True상태)가 아니어야 <Nozzle>
                    text: leftSyringe ==false && extrudersModel.items[tabBar.currentIndex].name === "Left" ? "Nozzle Guage" : "Needle Gauge"

                    verticalAlignment: Text.AlignVCenter
                    font: UM.Theme.getFont("default")
                    color: UM.Theme.getColor("text")
                    height: parent.height
                    width: selectors.textWidth
                    renderType: Text.NativeRendering
                }

                OldControls.ToolButton
                {
                    id: variantSelection
                    text: Cura.MachineManager.activeStack != null ? Cura.MachineManager.activeStack.variant.name : ""
                    tooltip: text
                    height: parent.height
                    width: selectors.controlWidth
                    style: UM.Theme.styles.print_setup_header_button
                    activeFocusOnPress: true
                    enabled: enabledCheckbox.checked

                    menu: Cura.NozzleMenu { extruderIndex: Cura.ExtruderManager.activeExtruderIndex }
                }
            }

            Row // Print temperature
            {
                height: UM.Theme.getSize("print_setup_big_item").height

                Cura.NumericTextFieldWithUnit  
                {
                    id: materialPrintTemperatureField
                    containerStackId: machineStackId
                    settingKey: "material_print_temperature"
                    settingStoreIndex: propertyStoreIndex
                    labelText: (leftSyringe ==false && extrudersModel.items[tabBar.currentIndex].name === "Left" ? "Nozzle" : "Needle") + " Temp."
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth *2.3
                    controlWidth: base.controlWidth *2
                    unitText: catalog.i18nc("@label", "°C")

                    forceUpdateOnChangeFunction: forceUpdateFunction
                    afterOnEditingFinishedFunction: manager.updateHasMaterialsMetadata
                }
            }

            Row // bed temperature
            {
                height: UM.Theme.getSize("print_setup_big_item").height

                Cura.NumericTextFieldWithUnit  
                {
                    id: materialBedTemperatureField
                    containerStackId: machineStackId
                    settingKey: "material_bed_temperature"
                    settingStoreIndex: propertyStoreIndex
                    labelText: catalog.i18nc("@label", "Build Plate Temp.")
                    labelFont: base.labelFont
                    labelWidth: base.labelWidth *2.3
                    controlWidth: base.controlWidth *2
                    unitText: catalog.i18nc("@label", "°C")

                    forceUpdateOnChangeFunction: forceUpdateFunction
                    afterOnEditingFinishedFunction: manager.updateHasMaterialsMetadata
                }
            }

            Row
            {
                id: warnings
                height: visible ? childrenRect.height : 0
                visible: buildplateCompatibilityError || buildplateCompatibilityWarning

                property bool buildplateCompatibilityError: !Cura.MachineManager.variantBuildplateCompatible && !Cura.MachineManager.variantBuildplateUsable
                property bool buildplateCompatibilityWarning: Cura.MachineManager.variantBuildplateUsable

                // This is a space holder aligning the warning messages.
                Label
                {
                    text: ""
                    width: selectors.textWidth
                    renderType: Text.NativeRendering
                }

                Item
                {
                    width: selectors.controlWidth
                    height: childrenRect.height

                    UM.RecolorImage
                    {
                        id: warningImage
                        anchors.left: parent.left
                        source: UM.Theme.getIcon("warning")
                        width: UM.Theme.getSize("section_icon").width
                        height: UM.Theme.getSize("section_icon").height
                        sourceSize.width: width
                        sourceSize.height: height
                        color: UM.Theme.getColor("material_compatibility_warning")
                        visible: !Cura.MachineManager.isCurrentSetupSupported || warnings.buildplateCompatibilityError || warnings.buildplateCompatibilityWarning
                    }

                    Label
                    {
                        id: materialCompatibilityLabel
                        anchors.left: warningImage.right
                        anchors.leftMargin: UM.Theme.getSize("default_margin").width
                        verticalAlignment: Text.AlignVCenter
                        width: selectors.controlWidth - warningImage.width - UM.Theme.getSize("default_margin").width
                        text: catalog.i18nc("@label", "Use glue for better adhesion with this material combination.")
                        font: UM.Theme.getFont("default")
                        color: UM.Theme.getColor("text")
                        visible: CuraSDKVersion == "dev" ? false : warnings.buildplateCompatibilityError || warnings.buildplateCompatibilityWarning
                        wrapMode: Text.WordWrap
                        renderType: Text.NativeRendering
                    }
                }
            }
        }
    }

    UM.SettingPropertyProvider
    {
        id: propertyProvider
        containerStack: Cura.MachineManager.activeMachine
        key: "material_print_temperature"
        watchedProperties: [ "value", "description" ]
        storeIndex: propertyStoreIndex
    }

    // Left Extruder Type
    UM.SettingPropertyProvider
    {
        id: leftExtruderType
        containerStack: Cura.MachineManager.activeMachine
        key: "left_extruder_type"
        watchedProperties: [ "value" ]
        storeIndex: propertyStoreIndex
    }
}
