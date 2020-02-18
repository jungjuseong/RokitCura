import QtQuick 2.6
import QtQuick.Controls 2.0
import QtQuick.Controls 1.1 as OldControls

import Cura 1.0 as Cura
import UM 1.3 as UM


OldControls.ToolButton
{
    id: materialSelection

    property bool valueError: Cura.MachineManager.activeStack !== null ? Cura.ContainerManager.getContainerMetaDataEntry(Cura.MachineManager.activeStack.material.id, "compatible", "") !== "True" : true
    property bool valueWarning: !Cura.MachineManager.isActiveQualitySupported

    text: Cura.MachineManager.activeStack !== null ? Cura.MachineManager.activeStack.material.name : ""
    tooltip: text
    enabled: enabledCheckbox.checked

    height: parent.height

    style: UM.Theme.styles.print_setup_header_button
    activeFocusOnPress: true
    menu: Cura.RokitMaterialMenu
    {
        extruderIndex: Cura.ExtruderManager.activeExtruderIndex
        updateModels: materialSelection.visible
    }
}
