import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 2.3 as Controls2

import UM 1.2 as UM
import Cura 1.0 as Cura


Rectangle {
    id: wellCircles


    property var holes: { 
        rows: 8 
        cols: 12 
        diameter: diameter0 / 4 
    } 

    property var spacing: UM.Theme.getSize("thin_margin").height 
    property var color: UM.Theme.getColor("rokit_build_plate")
    property var borderColor: UM.Theme.getColor("rokit_build_plate_border")
    
    width: childrenRect.width
    height : childrenRect.height
    anchors { centerIn: parent }

    Column {
        spacing: UM.Theme.getSize("thin_margin").height
        Repeater {
            model: holes.rows
            Row {
                spacing: spacing                   
                Repeater {
                    model: holes.cols
                    Rectangle {
                        width: holes.diameter
                        height: holes.diameter
                        radius: holes.diameter / 2
                        color: color
                        border.width : 1
                        border.color: borderColor
                    }
                }                 
            }
        }
    }
}
