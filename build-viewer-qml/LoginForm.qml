import QtQuick 2.0
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.1
import "."

Rectangle {
    property string connectHost: "localhost"
    property int connectPort: 5000;

    signal backgroundTouched();
    signal connectPressed();

    id: rectangle1
    color: "#b3000000"
    opacity: 0

    MouseArea{
        id: backgroundTouch
        x: parent.width
        width: parent.width
        height: parent.height
        onClicked: backgroundTouched()
    }

    Rectangle {
        color: GlobalData.backgroundBase
        id: loginBox
        width: parent.width
        y: parent.height
        height: 100

        MouseArea{
            id: touchGrabber
            x: parent.width
            width: parent.width
            height: parent.height
        }

        Rectangle {
            x: 0
            y: 0
            width: parent.width
            height: 2
            color: "black"
        }

        GridLayout {
            id: gridLayout1
            anchors.fill: parent
            flow: GridLayout.LeftToRight
            rows: 2
            columns: 2

            anchors.leftMargin: 10
            anchors.rightMargin: 10
            anchors.topMargin: 10
            anchors.bottomMargin: 10

            TextField {
                id: textField1
                text: connectHost
                placeholderText: qsTr("Host")
            }

            TextField {
                id: textField2
                text: connectPort
                placeholderText: qsTr("Port")
            }

            Item {
                width: 10
                height: 10
            }

            Button {
                id: button1
                text: qsTr("Connect")
                onClicked: {
                    connectPort = textField2.text
                    connectHost = textField1.text
                    connectPressed()
                }
            }
        }
    }
    states: [
        State {
            name: "compact"

            PropertyChanges {
                target: rectangle1
                opacity: 1
            }

            PropertyChanges {
                target: loginBox
                height: 100

                x: rectangle1.left
                y: rectangle1.height-height
            }

            PropertyChanges {
                target: backgroundTouch
                x: 0
            }

            PropertyChanges {
                target: touchGrabber
                x: 0
            }
        },
        State {
            name: "space"

            PropertyChanges {
                target: rectangle1
                opacity: 1
            }

            PropertyChanges {
                target: loginBox
            }
        }
    ]

    transitions: [
        Transition {
            from: "*"
            to: "compact"
            NumberAnimation { properties: "y";
                easing.type: Easing.InOutQuad; duration: 200 }
            NumberAnimation { properties: "opacity";
                easing.type: Easing.InOutQuad; duration: 200 }
        },
        Transition {
            from: "*"
            to: "default"
            NumberAnimation { properties: "y";
                easing.type: Easing.InOutQuad; duration: 200 }
            NumberAnimation { properties: "opacity";
                easing.type: Easing.InOutQuad; duration: 200 }
        }
    ]
}
