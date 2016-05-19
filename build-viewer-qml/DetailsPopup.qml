import QtQuick 2.0
import QtQuick.Controls 1.4
import QtQuick.Window 2.0

Rectangle {
    function toggleShow()
    {
        if(rectangle1.state != "shown")
            rectangle1.state = "shown"
        else
            rectangle1.state = "default"
    }

    id: rectangle1
    property string platform: "?";
    property string host: "?";
    property string commit: "?";
    property int status: 0;
    property int build_id: 0;
    property string timestamp: "?";
    property bool has_binary: false;

    property real coverage: 0.80;

    signal downloadPressed(int build_id);
    signal viewLogPressed(int build_id);

    color: "#4c000000"
    opacity: 0

    MouseArea{
        id: mouseArea1
        x: parent.width
        width: parent.width
        height: parent.height

        onClicked: toggleShow()

        Rectangle {
            id: rectangle2
            x: parent.width
            width: parent.width*coverage
            height: parent.height

            MouseArea{
                anchors.fill: parent

                Rectangle {
                    id: border
                    width: 2
                    color: "#000000"
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                }

                Item {
                    id: item1
                    anchors.fill: parent
                    anchors.rightMargin: 10
                    anchors.bottomMargin: 10
                    anchors.topMargin: 10
                    anchors.leftMargin: 10

                    Label {
                        id: title
                        text: qsTr("Build information")
                        font.bold: true
                        font.pointSize: 14 * scalingCoeff
                    }

                    Grid {
                        anchors.bottomMargin: 10
                        anchors.top: title.bottom
                        anchors.topMargin: 15
                        anchors.bottom: dlButton.top
                        anchors.left: parent.left
                        anchors.right: parent.right
                        columns: 2
                        spacing: 10
                        flow: Grid.LeftToRight

                        Label {
                            text: qsTr("Platform")
                            font.bold: true
                            font.pointSize: 12 * scalingCoeff
                        }

                        Label {
                            text: platform
                            font.pointSize: 12 * scalingCoeff
                        }

                        Label {
                            text: qsTr("Host")
                            font.bold: true
                            font.pointSize: 12 * scalingCoeff
                        }

                        Label {
                            text: host
                            font.pointSize: 12 * scalingCoeff
                        }

                        Label {
                            text: qsTr("Commit")
                            font.pointSize: 12 * scalingCoeff
                            font.bold: true
                        }

                        Label {
                            text: commit
                            font.pointSize: 12 * scalingCoeff
                        }

                        Label {
                            text: qsTr("Status")
                            font.bold: true
                            font.pointSize: 12 * scalingCoeff
                        }

                        Label {
                            text: (status == 0) ? qsTr("Successful") : qsTr("Failure")
                            font.pointSize: 12 * scalingCoeff
                        }

                        Label {
                            text: qsTr("Build ID")
                            font.bold: true
                            font.pointSize: 12 * scalingCoeff
                        }

                        Label {
                            text: build_id
                            font.pointSize: 12 * scalingCoeff
                        }

                        Label {
                            text: qsTr("Timestamp")
                            font.bold: true
                            font.pointSize: 12 * scalingCoeff
                        }

                        Label {
                            text: timestamp
                            font.pointSize: 12 * scalingCoeff
                        }

                    }

                    Button {
                        id: dlButton
                        visible: has_binary
                        text: qsTr("Download Release")
                        anchors.right: parent.right
                        anchors.left: parent.left
                        anchors.bottom: logButton.top
                        anchors.bottomMargin: 10

                        onClicked: downloadPressed(build_id)
                    }

                    Button {
                        id: logButton
                        text: qsTr("View Log")
                        anchors.right: parent.right
                        anchors.left: parent.left
                        anchors.bottom: parent.bottom

                        onClicked: viewLogPressed(build_id)
                    }
                }
            }
        }
    }
    states: [
        State {
            name: "shown"

            PropertyChanges {
                target: rectangle1
                opacity: 1
            }

            PropertyChanges {
                target: mouseArea1
                x: 0
            }

            PropertyChanges {
                target: rectangle2
                x: parent.width*(1.0-coverage)
            }
        }
    ]

    transitions: [
        Transition {
            from: "*"
            to: "shown"
            NumberAnimation { properties: "x";
                easing.type: Easing.InOutQuad; duration: 200 }
            NumberAnimation { properties: "opacity";
                easing.type: Easing.InOutQuad; duration: 200 }
        },
        Transition {
            from: "*"
            to: "default"
            NumberAnimation { properties: "x";
                easing.type: Easing.InOutQuad; duration: 200 }
            NumberAnimation { properties: "opacity";
                easing.type: Easing.InOutQuad; duration: 200 }
        }
    ]
}
