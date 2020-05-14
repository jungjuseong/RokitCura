import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 2.3 as Controls2

import UM 1.2 as UM
import Cura 1.0 as Cura

Rectangle {
    id: wellCircles

    property var base_diameter: UM.Theme.getSize("rokit_well_plate_diameter").width
    property var holes: [2, 3, 1]  // row, cols, size denominator

    property var spacing: UM.Theme.getSize("thin_margin").height 
    property var color: UM.Theme.getColor("rokit_build_plate")
    property var borderColor: UM.Theme.getColor("rokit_build_plate_border")
    
    width: childrenRect.width
    height : childrenRect.height
    anchors { centerIn: parent }

    Column {
        spacing: wellCircles.spacing * holes[2]
        Repeater {
            model: holes[0]
            Row {
                spacing: wellCircles.spacing * holes[2]                      
                Repeater {
                    model: holes[1]
                    Rectangle {
                        width: base_diameter * holes[2]
                        height: base_diameter * holes[2]
                        radius: base_diameter * holes[2] / 2
                        color: wellCircles.color
                        border.width : 1
                        border.color: wellCircles.borderColor
                    }
                }                 
            }
        }
    }
}
