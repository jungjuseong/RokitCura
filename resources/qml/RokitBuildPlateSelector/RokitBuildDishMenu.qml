// Copyright (c) 2017 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 1.4

import UM 1.2 as UM
import Cura 1.0 as Cura

Menu {
    id: menu

    property string category: ""
    property string selected: (buildDishType.properties.value !== undefined) ? buildDishType.properties.value : ""

    Instantiator {
        model: Cura.RokitBuildDishModel { }
    
        MenuItem  {
            id: menuItem

            text: model.product_id 
            checkable: false
            checked: {
                var activeMachine = Cura.MachineManager.activeMachine
                if (activeMachine == null) {
                    return false
                }                
                return selected ===  model.product_id
            }
            //exclusiveGroup: group
            //enabled: true
            onTriggered: {
                selected = model.product_id
                buildDishType.setPropertyValue("value", selected)

                preview.product_id = selected

                CuraApplication.writeToLog("i", 'selected.substr(0,10):'+ selected.substr(0,10))

                if (selected.substr(0,10) == "Well Plate") {
                    //var extruder = Cura.MachineManager.activeMachine.extruderList[0]
                    Cura.MachineManager.setExtruderEnabled(0, false)
                }
                else {
                    Cura.MachineManager.setExtruderEnabled(0, true)

                }
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
    
    UM.SettingPropertyProvider {
        id: buildDishType
        containerStack: Cura.MachineManager.activeMachine
        key: "machine_build_dish_type"
        watchedProperties: [ "value" ]
        storeIndex: 0
    }
}