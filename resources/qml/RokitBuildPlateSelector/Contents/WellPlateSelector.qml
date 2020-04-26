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
    dishModel: WellPlateModel {}
    
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
                            height : UM.Theme.getSize("rokit_well_plate_diameter").width
                            radius: width / 2
                            color: UM.Theme.getColor("rokit_build_plate")
                            border.width : 1
                            border.color: UM.Theme.getColor("rokit_build_plate_border")
                        }
                    }                  
                }
            }
        }
    }
}

