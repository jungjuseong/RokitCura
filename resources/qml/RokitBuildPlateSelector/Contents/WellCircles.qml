import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 2.3 as Controls2

import UM 1.2 as UM
import Cura 1.0 as Cura


Rectangle {
    id: wellCircles

    property var selectedWells: "6"
    property var rowHoles: 2
    property var columnHoles: 3
    property var diameter: {
        UM.Theme.getSize("rokit_well_plate_diameter").width
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
            model: wellCircles.rowHoles
            Row {
                spacing: wellCircles.spacing                        
                Repeater {
                    model: wellCircles.columnHoles
                    Rectangle {
                        width: wellCircles.diameter
                        height: wellCircles.diameter
                        radius: wellCircles.diameter / 2
                        color: wellCircles.color
                        border.width : 1
                        border.color: wellCircles.borderColor
                    }
                }                 
            }
        }
    }
}
