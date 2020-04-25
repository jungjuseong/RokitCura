import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 2.3 as Controls2

import UM 1.2 as UM
import Cura 1.0 as Cura
import QtQuick.Layouts 1.3

import "../../Widgets"
import "./model"

BuildPlateSelector {
      
    Rectangle {
        width: childrenRect.width
        height : childrenRect.height
        anchors { centerIn: parent }
        Column {
            spacing: UM.Theme.getSize("thin_margin").height
            Repeater {
                model: 2
                Row {
                    spacing: UM.Theme.getSize("thin_margin").height                        
                    Repeater {
                        model: 3
                        Rectangle {
                            width : UM.Theme.getSize("rokit_well_plate_diameter").width
                            height : width
                            radius: width*0.5
                            color: UM.Theme.getColor("rokit_build_plate")
                            border.width : 1
                            border.color: UM.Theme.getColor("rokit_build_plate_border")
                        }
                    }                  
                }
            }
        }
    }

    // Item {
    //     id: wellPlateButtons
    //     anchors
    //     {
    //         left: parent.left
    //         leftMargin: UM.Theme.getSize("default_margin").width
    //         bottom: parent.bottom
    //         horizontalCenter: plate1.horizontalCenter
    //     }
    //     spacing: 0.5

    //     ExclusiveGroup { id: wellPlateExclusive }

    //     Repeater {
    //         model: WellPlateModel {
    //             id: dishModel
    //         }            

    //         delegate: Button {                    
    //             text: model.text
    //             height: UM.Theme.getSize("rokit_well_plate_button").height
    //             width: UM.Theme.getSize("rokit_well_plate_button").width
    //             exclusiveGroup: wellPlateExclusive
    //             checkable: true
                
    //             onClicked: {
    //                 var attributes = dishModel.attributes[index]

    //                 machineWidth.setPropertyValue("value", attributes.width)
    //                 machineDepth.setPropertyValue("value", attributes.depth)
    //                 machineHeight.setPropertyValue("value", attributes.height)
    //                 machineShape.setPropertyValue("value", attributes.shape)

    //                 buildPlateType.setPropertyValue("value", "Well Plate:" + model.get(index).text)

    //                 afterOnEditingFinishedFunction()
    //             }  
    //         }
    //     }
    // }
    dishModel: WellPlateModel {}
}
