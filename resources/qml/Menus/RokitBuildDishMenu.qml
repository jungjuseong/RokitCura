// Copyright (c) 2017 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 1.4

import UM 1.2 as UM
import Cura 1.0 as Cura

Menu {
    id: menu
    title: "Dish"

    property int index: 0
    property string category: ""

    Instantiator {
        model: Cura.RokitBuildDishModel { }
    
        MenuItem  {

            text: model.product_id 
            checkable: false
            checked: {
                var activeMachine = Cura.MachineManager.activeMachine
                if (activeMachine == null) {
                    return false
                }
                return (index === -1) ? false : buildDishType.properties.value ===  model.product_id
            }
            exclusiveGroup: group
            enabled: true
            onTriggered: {
                buildDishType.setPropertyValue("value", model.product_id)
            }
        }
        onObjectAdded: {
            const category = object.text.split(":")[0]
            if (object.text.indexOf(menu.category) !== -1) {
                menu.insertItem(index, object);
            }
        }
        onObjectRemoved: menu.removeItem(object);
    }

    // "Build dish type"
    UM.SettingPropertyProvider {
        id: buildDishType
        containerStack: Cura.MachineManager.activeMachine
        key: "machine_build_dish_type"
        watchedProperties: [ "value" ]
        storeIndex: 0
    }
}
