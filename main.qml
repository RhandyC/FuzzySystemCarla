import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    property alias foggy_level: slider_foggy_level.value
    property alias brightness_level: slider_brightness_level.value
    property alias limit_speed: slider_limit_speed.value
    property alias state_car: slider_state_car.value
    
    id:root
    title: qsTr("Entrees simulee")
    width:520
    height: 320
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
        value: 1
    }
    Text {
        x: 400
        y: 57
        text: slider_brightness_level.value.toFixed(2)
        color: "gold"
    }
    Text {
        x: 39
        text: qsTr("Limit Speed")
        color: "gold"
        y:92
    }
    Slider {
        id: slider_limit_speed
        width: 200
        height: 20
        to: 130
        x: 189
        y:92
        value: 130
    }
    Text {
        x: 400
        y: 92
        text: slider_limit_speed.value.toFixed(0) + " km/h"
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
        y: 260
        text: qsTr("Apply")
    }
    Button {
        id: button1
        x: 300
        y: 260
        text: qsTr("Reset")
        onClicked: {
            slider_foggy_level.value = 0;
            slider_brightness_level.value = 1; 
            slider_consomation.value = 10;
            slider_limit_speed.value = 130;
            slider_state_car.value = 0;
            prudent_option.checked = true;
        }
    }
    RadioButton {
        id: prudent_option
        x: 40
        y: 200
        checked: true
        contentItem: Text {
            text: prudent_option.text
            color: "white"
            leftPadding: prudent_option.indicator.width + prudent_option.spacing
            verticalAlignment: Text.AlignVCenter
        }
        text: qsTr("Prudent")
    }
    RadioButton {
        id: presse_option
        x: 200
        y: 200
        text: qsTr("Pressé")
        contentItem: Text {
            text: presse_option.text
            color: "white"
            leftPadding: presse_option.indicator.width + presse_option.spacing
            verticalAlignment: Text.AlignVCenter
        }
    }
    RadioButton {
        id: hloi_option
        x: 360
        y: 200
        text: qsTr("Hors loi")
        contentItem: Text {
            text: hloi_option.text
            color: "white"
            leftPadding: hloi_option.indicator.width + hloi_option.spacing
            verticalAlignment: Text.AlignVCenter
        }
    }

    Button {
        text: "Output"
        x: 420
        y: 280
        onClicked: {
            output_window.show()
        }
    }

    ApplicationWindow {
        id: output_window
        title: qsTr("Entrees simulee")
        width:520
        height: 350
        color: "black"

        Label {
            id: result1
            text : "Resultat"
            objectName: "labelCo"
            color: "gold"
            x: 400
            anchors.verticalCenter: parent.verticalCenter
        }

        // Rectangles decoratif

        Rectangle {
            width: 100
            height: 60
            x: 50
            y: 40
            color: "gray"
            border.color: "white"
            border.width: 2
            Text {
                text: qsTr("Sisteme flou 1")
                color: "gold"
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        Rectangle {
            width: 100
            height: 60
            x: 50
            y: 140
            color: "gray"
            border.color: "white"
            border.width: 2
            Text {
                text: qsTr("Sisteme flou 2")
                color: "gold"
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        Rectangle {
            width: 100
            height: 60
            x: 50
            y: 240
            color: "gray"
            border.color: "white"
            border.width: 2
            Text {
                text: qsTr("Sisteme flou 3")
                color: "gold"
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        Rectangle {
            width: 100
            height: 60
            x: 250
            y: 80
            color: "gray"
            border.color: "white"
            border.width: 2
            Text {
                text: qsTr("Sisteme flou 4")
                color: "gold"
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        Rectangle {
            width: 100
            height: 60
            x: 250
            y: 180
            color: "gray"
            border.color: "white"
            border.width: 2
            Text {
                text: qsTr("Sisteme flou 5")
                color: "gold"
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }
    

}

