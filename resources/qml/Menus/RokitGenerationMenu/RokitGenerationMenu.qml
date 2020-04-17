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

    property var extrudersModel: Cura.ExtrudersModel{} // CuraApplication.getExtrudersModel()

    UM.I18nCatalog
    {
        id: catalog
        name: "cura"
    }

    enum GenerationMethod
    {
        Auto,
        Custom
    }

    contentPadding: UM.Theme.getSize("default_lining").width
    enabled: Cura.MachineManager.activeMachine.hasMaterials || Cura.MachineManager.activeMachine.hasVariants || Cura.MachineManager.activeMachine.hasVariantBuildplates; //Only let it drop down if there is any configuration that you could change.

    headerItem: Cura.IconWithText
    {
        text: "Generation"
        source: UM.Theme.getIcon("check")
        font: UM.Theme.getFont("medium")
        iconColor: UM.Theme.getColor("machine_selector_printer_icon")
        iconSize: source != "" ? UM.Theme.getSize("machine_selector_icon").width: 0
    }

    contentItem: Column
    {
        id: popupItem
        width: UM.Theme.getSize("configuration_selector").width
        height: implicitHeight  // ExpandableComponent will try to use this to determine the size of the background of the pop-up.
        padding: UM.Theme.getSize("default_margin").height
        spacing: UM.Theme.getSize("default_margin").height

        property bool is_connected: false  // If current machine is connected to a printer. Only evaluated upon making popup visible.
        property int configuration_method: RokitGenerationMenu.GenerationMethod.Custom  // Type of configuration being used. Only evaluated upon making popup visible.
        property int manual_selected_method: -1  // It stores the configuration method selected by the user. By default the selected method is

        onVisibleChanged:
        {
            configuration_method = RokitGenerationMenu.GenerationMethod.Custom
        }

        Item
        {
            width: parent.width - 2 * parent.padding
            height: rokitGeneration.height + actionPanelWidget.height + UM.Theme.getSize("default_margin").height * 2

            RokitGeneration
            {
                id: rokitGeneration
                visible: true
            }

            Cura.ActionPanelWidget
            {
                id: actionPanelWidget
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.rightMargin: UM.Theme.getSize("thick_margin").width
                anchors.bottomMargin: UM.Theme.getSize("thick_margin").height
            }
        }


        
    }

    Connections
    {
        target: Cura.MachineManager
        onGlobalContainerChanged: popupItem.manual_selected_method = -1  // When switching printers, reset the value of the manual selected method
    }


}
