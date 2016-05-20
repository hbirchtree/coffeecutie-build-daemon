import QtQuick 2.0
import QtQuick.Controls 1.4
import QtQuick.Window 2.0
import "."

Rectangle {
    function toggleShow()
    {
        if(backgroundShroud.state != "shown")
        {
            backgroundShroud.state = "shown"
        }
        else
        {
            backgroundShroud.state = "default"
        }
    }

    id: backgroundShroud
    property string platform: "?";
    property string host: "?";
    property string commit: "?";
    property int status: 0;
    property int build_id: 0;
    property string timestamp: "?";
    property bool has_binary: false;

    property real coverage: 0.80;

    signal backgroundTouched()
    signal downloadPressed(int build_id);
    signal viewLogPressed(int build_id);

    color: "#b3000000"
    opacity: 0

    MouseArea{
        id: b_s_touch
        x: parent.width
        y: 0
        width: parent.width
        height: parent.height
        onClicked: backgroundTouched()
    }

    Rectangle {
        id: panel
        x: parent.width
        width: parent.width*coverage
        height: parent.height
        gradient: Gradient {
            GradientStop {
                position: 0.00;
                color: GlobalData.backgroundHighlight;
            }
            GradientStop {
                position: (14 * GlobalData.scalingCoeff)/height;
                color: GlobalData.backgroundBase;
            }
        }

        Rectangle{
            x: 0
            width: 2
            height: parent.height
            color: GlobalData.highlight
        }

        Item {
            MouseArea{
                id: p_touch
                anchors.fill: parent
            }
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
                font.pointSize: 14 * GlobalData.scalingCoeff
                color: GlobalData.textBase
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
                    font.pointSize: 12 * GlobalData.scalingCoeff
                    color: GlobalData.textBase
                }

                Label {
                    text: platform
                    font.pointSize: 12 * GlobalData.scalingCoeff
                    color: GlobalData.textBase
                }

                Label {
                    text: qsTr("Host")
                    font.bold: true
                    font.pointSize: 12 * GlobalData.scalingCoeff
                    color: GlobalData.textBase
                }

                Label {
                    text: host
                    font.pointSize: 12 * GlobalData.scalingCoeff
                    color: GlobalData.textBase
                }

                Label {
                    text: qsTr("Commit")
                    font.pointSize: 12 * GlobalData.scalingCoeff
                    font.bold: true
                    color: GlobalData.textBase
                }

                Label {
                    text: commit
                    font.pointSize: 12 * GlobalData.scalingCoeff
                    color: GlobalData.textBase
                }

                Label {
                    text: qsTr("Status")
                    font.bold: true
                    font.pointSize: 12 * GlobalData.scalingCoeff
                    color: GlobalData.textBase
                }

                Label {
                    text: (status == 0) ? qsTr("Successful") : qsTr("Failure")
                    font.pointSize: 12 * GlobalData.scalingCoeff
                    color: GlobalData.textBase
                }

                Label {
                    text: qsTr("Build ID")
                    font.bold: true
                    font.pointSize: 12 * GlobalData.scalingCoeff
                    color: GlobalData.textBase
                }

                Label {
                    text: build_id
                    font.pointSize: 12 * GlobalData.scalingCoeff
                    color: GlobalData.textBase
                }

                Label {
                    text: qsTr("Timestamp")
                    font.bold: true
                    font.pointSize: 12 * GlobalData.scalingCoeff
                    color: GlobalData.textBase
                }

                Label {
                    text: timestamp
                    font.pointSize: 12 * GlobalData.scalingCoeff
                    color: GlobalData.textBase
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
    states: [
        State {
            name: "shown"

            PropertyChanges {
                target: backgroundShroud
                opacity: 1
            }

            PropertyChanges {
                target: panel
                x: parent.width*(1.0-coverage)
            }

            PropertyChanges {
                target: b_s_touch
                x: 0
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
