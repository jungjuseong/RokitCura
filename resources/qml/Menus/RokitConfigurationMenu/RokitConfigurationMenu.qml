// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 2.3
import QtQuick.Controls.Styles 1.4

import UM 1.2 as UM
import Cura 1.0 as Cura


/**
 * Menu that allows you to select the configuration of the current printer, such
 * as the nozzle sizes and materials in each extruder.
 */
Cura.ExpandablePopup
{
    id: base

    property var extrudersModel: CuraApplication.getExtrudersModel()

    UM.I18nCatalog
    {
        id: catalog
        name: "cura"
    }

    contentPadding: UM.Theme.getSize("default_lining").width
    enabled: Cura.MachineManager.activeMachine.hasMaterials || Cura.MachineManager.activeMachine.hasVariants || Cura.MachineManager.activeMachine.hasVariantBuildplates; //Only let it drop down if there is any configuration that you could change.

    headerItem: Item
    {
        // Horizontal list that shows the extruders and their materials
        ListView
        {
            id: extrudersList

            orientation: ListView.Horizontal
            anchors.fill: parent
            model: extrudersModel
            visible: Cura.MachineManager.activeMachine.hasMaterials

            delegate: Item
            {
                height: parent.height
                width: Math.round(ListView.view.width / extrudersModel.count)

                // Extruder icon. Shows extruder index and has the same color as the active material.
                Cura.ExtruderIcon
                {
                    id: extruderIcon
                    materialColor: model.color
                    extruderEnabled: model.enabled
                    height: parent.height
                    width: height
                }

                // Label for the brand of the material
                Label
                {
                    id: typeAndBrandNameLabel

                    text: model.material // model.material_brand + " " + model.material
                    elide: Text.ElideRight
                    font: UM.Theme.getFont("default")
                    color: UM.Theme.getColor("text")
                    renderType: Text.NativeRendering

                    anchors
                    {
                        top: extruderIcon.top
                        left: extruderIcon.right
                        leftMargin: UM.Theme.getSize("default_margin").width
                        right: parent.right
                        rightMargin: UM.Theme.getSize("default_margin").width
                    }
                }
                // Label that shows the name of the variant
                Label
                {
                    id: variantLabel

                    visible: Cura.MachineManager.activeMachine.hasVariants

                    text: model.variant
                    elide: Text.ElideRight
                    font: UM.Theme.getFont("default_bold")
                    color: UM.Theme.getColor("text")
                    renderType: Text.NativeRendering

                    anchors
                    {
                        left: extruderIcon.right
                        leftMargin: UM.Theme.getSize("default_margin").width
                        top: typeAndBrandNameLabel.bottom
                        right: parent.right
                        rightMargin:  UM.Theme.getSize("default_margin").width
                    }
                }
            }
        }

        // Placeholder text if there is a configuration to select but no materials (so we can't show the materials per extruder).
        Label
        {
            text: catalog.i18nc("@label", "Select configuration")
            elide: Text.ElideRight
            font: UM.Theme.getFont("medium")
            color: UM.Theme.getColor("text")
            renderType: Text.NativeRendering

            visible: !Cura.MachineManager.activeMachine.hasMaterials && (Cura.MachineManager.activeMachine.hasVariants || Cura.MachineManager.activeMachine.hasVariantBuildplates)

            anchors
            {
                left: parent.left
                leftMargin: UM.Theme.getSize("default_margin").width
                verticalCenter: parent.verticalCenter
            }
        }
    }

    contentItem: Column
    {
        id: popupItem
        width: UM.Theme.getSize("configuration_selector").width
        height: implicitHeight  // Required because ExpandableComponent will try to use this to determine the size of the background of the pop-up.
        padding: UM.Theme.getSize("default_margin").height
        spacing: UM.Theme.getSize("default_margin").height

        property bool is_connected: false  // If current machine is connected to a printer. Only evaluated upon making popup visible.
        property int manual_selected_method: -1  // It stores the configuration method selected by the user. By default the selected method is

        Item
        {
            width: parent.width - 2 * parent.padding
            height: customConfiguration.height

            CustomConfiguration
            {
                id: customConfiguration
            }
        }
    }
}
