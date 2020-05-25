import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 2.3 as Controls2

import UM 1.2 as UM
import Cura 1.0 as Cura

Rectangle {
    id: base

    visible: category === "Well Plate"
    width: childrenRect.width
    height: childrenRect.height
    anchors.centerIn: parent

    property string product_id: ""

    property var diameter: UM.Theme.getSize("rokit_well_plate_diameter").width
    property int rows: 2
    property int cols: 3
    property var size_factor: 1
    property int radius: diameter / 2
    
    property var spacing: UM.Theme.getSize("thin_margin").height 
    property var color: UM.Theme.getColor("rokit_build_plate")
    property var borderColor: UM.Theme.getColor("rokit_build_plate_border")
    
    property var circlesInfo: {
        const category = product_id.split(":")[0]
        const numberOfCircles = product_id.split(":")[1]

        console.log(product_id)

        var circles = {}
        circles.rows = 1
        circles.cols = 1
        circles.size_factor = 2

        if (category === "Well Plate") {
            switch (numberOfCircles) {
                case "96":
                    circles.rows = 8, circles.cols = 12, circles.size_factor = 1/4
                    break
                case "48":
                    circles.rows = 6, circles.cols = 8, circles.size_factor = 1/3
                    break
                case "24":
                    circles.rows = 4, circles.cols = 6, circles.size_factor = 1/2
                    break
                case "12":
                    circles.rows = 3, circles.cols = 4, circles.size_factor = 2/3
                    break
                default:
                    circles.rows = 2 , circles.cols = 3, circles.size_factor = 1
            }
        }
        circles.radius = (category === "Culture Slide") ? 0 : (base.diameter * circles.size_factor) / 2

        return circles
    }

    Column {

        spacing: base.spacing * circlesInfo.size_factor
        Repeater {
            model: circlesInfo.rows
            Row {
                spacing: base.spacing * circlesInfo.size_factor                      
                Repeater {
                    model: circlesInfo.cols
                    Rectangle {
                        width: base.diameter * circlesInfo.size_factor
                        height: base.diameter * circlesInfo.size_factor
                        radius: circlesInfo.radius
                        color: base.color
                        border.width : 1
                        border.color: base.borderColor
                    }
                }                 
            }
        }
    }
}
