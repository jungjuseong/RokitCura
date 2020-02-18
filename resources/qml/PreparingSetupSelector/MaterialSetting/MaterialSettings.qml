// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4

import UM 1.2 as UM
import Cura 1.0 as Cura

Item
{
    id: materialSettings

    height: childrenRect.height + 2 * padding

    property Action configureSettings

    //property bool settingsEnabled: Cura.ExtruderManager.activeExtruderStackId || extrudersEnabledCount.properties.value == 1
    property real padding: UM.Theme.getSize("thick_margin").width

    Column
    {
        spacing: UM.Theme.getSize("wide_margin").height

        anchors
        {
            left: parent.left
            right: parent.right
            top: parent.top
            margins: parent.padding
        }

        // TODO
        property real firstColumnWidth: Math.round(width / 2)

        RecommendedQualityProfileSelector
        {
            width: parent.width
            // TODO Create a reusable component with these properties to not define them separately for each component
            labelColumnWidth: parent.firstColumnWidth
        }

        RokitGenericSelector
        {
            width: parent.width
            // TODO Create a reusable component with these properties to not define them separately for each component
            labelColumnWidth: parent.firstColumnWidth
        }
        RokitBioInkSelector
        {
            width: parent.width
            // TODO Create a reusable component with these properties to not define them separately for each component
            labelColumnWidth: parent.firstColumnWidth
        }

        Cura.SecondaryButton
        {
            id: addPrinterButton

            width: parent.width / 2
            leftPadding: UM.Theme.getSize("default_margin").width
            rightPadding: UM.Theme.getSize("default_margin").width
            text: catalog.i18nc("@button", "Material Management")
            // The maximum width of the button is half of the total space, minus the padding of the parent, the left
            // padding of the component and half the spacing because of the space between buttons.
            maximumWidth: UM.Theme.getSize("machine_selector_widget_content").width / 2 - parent.padding - leftPadding - parent.spacing / 2
            onClicked:
            {
                toggleContent()
                Cura.Actions.manageMaterials.trigger()
            }
        }
    }

    UM.SettingPropertyProvider
    {
        id: extrudersEnabledCount
        containerStack: Cura.MachineManager.activeMachine
        key: "extruders_enabled_count"
        watchedProperties: [ "value" ]
        storeIndex: 0
    }
}
