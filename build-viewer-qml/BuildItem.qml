import QtQuick 2.0
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.1
import QtQuick.Window 2.0
import "."

Item {
    function displayDetails()
    {
        delegateItemThingy.state = "expanded"
    }
    function hideDetails()
    {
        delegateItemThingy.state = "default"
    }
    function toggleDetails()
    {
        if(delegateItemThingy.state != "expanded")
            displayDetails()
        else
            hideDetails()
    }

    signal downloadPressed();
    signal logViewPressed();
    signal itemPressed();

    id: delegateItemThingy
    width: 300
    height: 40 * GlobalData.scalingCoeff

    Item {
        anchors.fill: parent

        Item {
            id: summaryBox
            height: 40 * GlobalData.scalingCoeff
            anchors.right: parent.right
            anchors.left: parent.left
            anchors.top: parent.top
            Rectangle {
                id: summaryIcon
                width: 40 * GlobalData.scalingCoeff
                height: 40 * GlobalData.scalingCoeff
                color: colorCode
                border.color: colorCode
                gradient: Gradient {
                    GradientStop {
                        position: 0.00;
                        color: "#ffffff"
                    }
                    GradientStop {
                        position: 0.50;
                        color: Qt.darker(colorCode,2.0);
                    }
                }
            }

            Column{
                anchors.left: summaryIcon.right
                anchors.leftMargin: 5
                anchors.right: parent.right
                anchors.rightMargin: 0
                Label {
                    id: summaryLabel
                    text: host + " | " + platform
                    font.bold: true
                    color: GlobalData.textBase
                }
                Label {
                    id: summarySubLabel
                    text: timest
                    color: GlobalData.textBase
                }
            }
        }

        Item {
            id: detailBox
            anchors.fill: parent
            opacity: 0
            x: 0
            y: 40 * GlobalData.scalingCoeff
            anchors.topMargin: 40 * GlobalData.scalingCoeff + 5

            GridLayout {
                anchors.fill: parent
                flow: GridLayout.LeftToRight
                rowSpacing: 5
                columns: 2

                Label {
                    font.italic: true
                    font.bold: true
                    text: qsTr("Commit")
                }
                Label {
                    text: commit
                }

                Label {
                    font.italic: true
                    font.bold: true
                    text: qsTr("Build ID")
                }
                Label {
                    text: bid
                }

                Label {
                    font.italic: true
                    font.bold: true
                    text: qsTr("Released")
                }
                Label {
                    text: has_bin ? qsTr("Yes") : qsTr("No")
                }

                Button {
                    id: button__log
                    text: qsTr("View Log")
                    onClicked: logViewPressed()
                    Layout.alignment: Qt.AlignLeft
                }

                Button {
                    id: button_dl
                    text: qsTr("Download")
                    onClicked: downloadPressed()
                    Layout.alignment: Qt.AlignRight
                }
            }
        }
    }

    states: [
        State {
            name: "expanded"

            PropertyChanges {
                target: delegateItemThingy
                height: 155
            }

            PropertyChanges {
                target: detailBox
                height: parent.height-(40 * GlobalData.scalingCoeff)
                opacity: 1
            }
        }
    ]

    transitions: [
        Transition {
            from: "*"
            to: "expanded"
            NumberAnimation { properties: "height";
                easing.type: Easing.InOutQuad; duration: 200 }
            NumberAnimation { properties: "opacity";
                easing.type: Easing.InOutQuad; duration: 200 }
        },
        Transition {
            from: "*"
            to: "default"
            NumberAnimation { properties: "height";
                easing.type: Easing.InOutQuad; duration: 200 }
            NumberAnimation { properties: "opacity";
                easing.type: Easing.InOutQuad; duration: 200 }
        }
    ]

    MouseArea {
        id: summaryBoxClicker
        anchors.fill: parent

        onClicked: {
            itemPressed()
        }
    }
}
