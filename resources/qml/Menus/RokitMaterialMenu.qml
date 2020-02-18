// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 1.4

import UM 1.2 as UM
import Cura 1.0 as Cura

Menu
{
    id: menu
    title: catalog.i18nc("@label:category menu label", "Material")

    property int extruderIndex: 0
    property string currentRootMaterialId:
    {
        var value = Cura.MachineManager.currentRootMaterialId[extruderIndex]
        return (value === undefined) ? "" : value
    }
    property var activeExtruder:
    {
        var activeMachine = Cura.MachineManager.activeMachine
        return (activeMachine === null) ? null : activeMachine.extruderList[extruderIndex]
    }
    property bool isActiveExtruderEnabled: activeExtruder === null ? false : activeExtruder.isEnabled

    property string activeMaterialId: activeExtruder === null ? false : activeExtruder.material.id

    property bool updateModels: true
    Cura.FavoriteMaterialsModel
    {
        id: favoriteMaterialsModel
        extruderPosition: menu.extruderIndex
        enabled: updateModels
    }

    Cura.GenericMaterialsModel
    {
        id: genericMaterialsModel
        extruderPosition: menu.extruderIndex
        enabled: updateModels
    }

    Instantiator
    {
        model: genericMaterialsModel
        delegate: MenuItem
        {
            text: model.name
            checkable: true
            enabled: isActiveExtruderEnabled
            checked: model.root_material_id === menu.currentRootMaterialId
            exclusiveGroup: group
            onTriggered: Cura.MachineManager.setMaterial(extruderIndex, model.container_node)
        }
        onObjectAdded: menu.insertItem(index, object)
        onObjectRemoved: menu.removeItem(index)
    }

    ExclusiveGroup
    {
        id: group
    }

    MenuSeparator {}

    MenuItem
    {
        action: Cura.Actions.manageMaterials
    }
}
