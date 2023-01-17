import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    property alias foggy_level: slider_foggy_level.value
    property alias brightness_level: slider_brightness_level.value
    property alias limit_speed: slider_behavior_driver.value
    property alias state_car: slider_state_car.value
    
    id:root
    title: qsTr("Entrees simulee")
    width:520
    height: 260
    color: "black"
    Text {
        x: 39
        y: 22
        text: qsTr("Foggy level")
        color: "gold"
    }
    Slider {
        id: slider_foggy_level
        objectName : "slider_foggy_level"
        width: 200
        height: 20
        x: 189
        y: 22
        to: 1
        value: 0
    }
    Text {
        x: 400
        y: 22
        text: slider_foggy_level.value.toFixed(2)
        color: "gold"
    }
    Text {
        x: 39
        text: qsTr("Brightness level")
        color: "gold"
        y:57
    }
    Slider {
        id: slider_brightness_level
        objectName : "slider_brightness_level"
        width: 200
        height: 20
        x: 189
        y:57
        to: 1
        value: 0.75
    }
    Text {
        x: 400
        y: 57
        text: slider_brightness_level.value.toFixed(2)
        color: "gold"
    }
    Text {
        x: 39
        text: qsTr("Behavior Driver")
        color: "gold"
        y:92
    }
    Slider {
        id: slider_behavior_driver
        objectName : "slider_behavior_driver"
        width: 200
        height: 20
        to: 1
        x: 189
        y:92
        value: 0
    }
    Text {
        x: 400
        y: 92
        text: slider_behavior_driver.value.toFixed(2)
        color: "gold"
    }
    Text {
        x: 39
        text: qsTr("State Car")
        color: "gold"
        y:127
    }
    Slider {
        id: slider_state_car
        objectName : "slider_state_car"
        width: 200
        height: 20
        to: 25
        x: 189
        y: 127
        value: 0
    }
    Text {
        x: 400
        y: 127
        text: slider_state_car.value.toFixed(0) + " annêes"
        color: "gold"
    }
    Text {
        x: 39
        text: qsTr("Consomation")
        color: "gold"
        y:162
    }
    Slider {
        id: slider_consomation
        objectName : "slider_consomation"
        width: 200
        height: 20
        to: 25
        x: 189
        y:162
        value: 10
    }
    Text {
        x: 400
        y: 162
        text: slider_consomation.value.toFixed(1) + " L/100km"
        color: "gold"
    }
    Button {
        id: button
        objectName : "Apply_Button"
        x: 120
        y: 200
        text: qsTr("Apply")
    }

    Button {
        id: button_center
        objectName : "Recenter_Button"
        x: 0
        y: 220
        text: qsTr("Recenter")
    }

    Button {
        id: button1
        x: 300
        y: 200
        text: qsTr("Reset")
        onClicked: {
            slider_foggy_level.value = 0;
            slider_brightness_level.value = 1; 
            slider_consomation.value = 10;
            slider_behavior_driver.value = 0;
            slider_state_car.value = 0;
        }
    }
    // RadioButton {
    //     id: prudent_option
    //     x: 40
    //     y: 200
    //     checked: true
    //     contentItem: Text {
    //         text: prudent_option.text
    //         color: "white"
    //         leftPadding: prudent_option.indicator.width + prudent_option.spacing
    //         verticalAlignment: Text.AlignVCenter
    //     }
    //     text: qsTr("Prudent")
    // }
    // RadioButton {
    //     id: presse_option
    //     x: 200
    //     y: 200
    //     text: qsTr("Pressé")
    //     contentItem: Text {
    //         text: presse_option.text
    //         color: "white"
    //         leftPadding: presse_option.indicator.width + presse_option.spacing
    //         verticalAlignment: Text.AlignVCenter
    //     }
    // }
    // RadioButton {
    //     id: hloi_option
    //     x: 360
    //     y: 200
    //     text: qsTr("Hors loi")
    //     contentItem: Text {
    //         text: hloi_option.text
    //         color: "white"
    //         leftPadding: hloi_option.indicator.width + hloi_option.spacing
    //         verticalAlignment: Text.AlignVCenter
    //     }
    // }

    Button {
        text: "Output"
        x: 420
        y: 220
        onClicked: {
            output_window.show()
        }
    }

    ApplicationWindow {
        id: output_window
        title: qsTr("Entrees simulee")
        width: 650
        height: 350
        color: "black"

        Label {
            id: foggy
            text : "Fogginess --------"
            color: "white"
            x: 20
            y: 40
        }

        Label {
            id: foggy_level
            text : "0.0"
            objectName: "foggy_level"
            color: "gold"
            x: 20
            y: 56
        }

        Label {
            id: brightness
            text : "Brightness --------"
            color: "white"
            x: 20
            y: 70
        }

        Label {
            id: brightness_level
            text : "1.0"
            objectName: "brightness_level"
            color: "gold"
            x: 20
            y: 86
        }

        Label {
            id: conso
            text : "Consommation ------"
            color: "white"
            x: 20
            y: 135
        }

        Label {
            id: conso_level
            text : "1.0"
            objectName: "conso_level"
            color: "gold"
            x: 20
            y: 151
        }

        Label {
            id: age_car
            text : "Age Car -----------"
            color: "white"
            x: 20
            y: 165
        }

        Label {
            id: age_car_level
            text : "1.0"
            objectName: "age_car_level"
            color: "gold"
            x: 20
            y: 181
        }

        Label {
            id: behavior
            text : "Behavior -----------"
            color: "white"
            x: 20
            y: 195
        }

        Label {
            id: behavior_level
            text : "1.0"
            objectName: "behavior_level"
            color: "gold"
            x: 20
            y: 211
        }

        Label {
            id: visibility
            text : "--------Visibility\n                 |\n                 |-------- "
            color: "white"
            x: 180
            y: 60
        }

        Label {
            id: visibility_level
            text : "1.0"
            objectName: "visibility_level"
            color: "gold"
            x: 220
            y: 76
        }

        Label {
            id: intrinsicSpeed
            text : "--------Intrinsic \n          Speed"
            color: "white"
            x: 180
            y: 160
        }

        Label {
            id: intrinsicSpeed_level
            text : "1.0"
            objectName: "intrinsicSpeed_level"
            color: "gold"
            x: 220
            y: 196
        }

        Label {
            id: conexion
            text : "|-----------"
            color: "white"
            x: 250
            y: 140
        }

        Label {
            id: accessibleSpeed
            text : "--------Accessible ----- \n          Speed"
            color: "white"
            x: 340
            y: 110
        }

        Label {
            id: accessibleSpeed_level
            text : "1.0"
            objectName: "accessibleSpeed_level"
            color: "gold"
            x: 380
            y: 146
        }


        Label {
            id: limitSpeed
            text : "Limit Speed\n        |\n        |"
            color: "white"
            x: 460
            y: 50
        }

        Label {
            id: limitSpeed_level
            text : "1.0"
            objectName: "limitSpeed_level"
            color: "gold"
            x: 460
            y: 66
        }
        
        Label {
            id: behavior2
            text : "       |\n       |\nBehavior"
            color: "white"
            x: 460
            y: 150
        }

        Label {
            id: behavior_level2
            text : "1.0"
            objectName: "behavior_level2"
            color: "gold"
            x: 460
            y: 198
        }
        

        Label {
            id: targetSpeed
            text : "------Target Speed"
            color: "white"
            x: 540
            y: 110
        }

        Label {
            id: targetSpeed_level
            text : "1.0"
            objectName: "targetSpeed_level"
            color: "gold"
            x: 570
            y: 126
        }

        // Rectangles decoratif

        Rectangle {
            width: 80
            height: 60
            x: 120
            y: 40
            color: "gray"
            border.color: "white"
            border.width: 2
            Text {
                text: qsTr("Sisteme\n  flou 1")
                color: "gold"
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        Rectangle {
            width: 80
            height: 75
            x: 120
            y: 140
            color: "gray"
            border.color: "white"
            border.width: 2
            Text {
                text: qsTr("Sisteme\n  flou 2")
                color: "gold"
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        Rectangle {
            width: 80
            height: 60
            x: 300-20
            y: 95
            color: "gray"
            border.color: "white"
            border.width: 2
            Text {
                text: qsTr("Sisteme\n  flou 3")
                color: "gold"
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        Rectangle {
            width: 80
            height: 60
            x: 460
            y: 95
            color: "gray"
            border.color: "white"
            border.width: 2
            Text {
                text: qsTr("Minimum\n  Speed")
                color: "gold"
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        // Rectangle {
        //     width: 100
        //     height: 60
        //     x: 250
        //     y: 180
        //     color: "gray"
        //     border.color: "white"
        //     border.width: 2
        //     Text {
        //         text: qsTr("Sisteme flou 5")
        //         color: "gold"
        //         anchors.horizontalCenter: parent.horizontalCenter
        //         anchors.verticalCenter: parent.verticalCenter
        //     }
        // }
    }
    

}

