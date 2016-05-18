import QtQuick 2.4
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.2
import BuildView 1.0

ApplicationWindow {
    title: qsTr("Build Viewer")
    visible: true
    onSceneGraphInitialized: data_source.update()

    BuildInfo {
        id: data_source
        server: "25.57.48.59"
        serverPort: 5000
        onFetchingChanged: {
            bform.loadIndicatorWidget.running = data_source.fetching
            bform.loadIndicatorWidget.visible = data_source.fetching
        }
    }

    BuildViewForm{
        id: bform
        anchors.fill: parent

        loadIndicatorWidget.running: data_source.fetching
        loadIndicatorWidget.visible: data_source.fetching

        ListView {
            id: listView1
            anchors.rightMargin: 5
            anchors.leftMargin: 5
            anchors.fill: parent
            spacing: 5
            delegate: Item {
                id: delegateItemThingy
                width: parent.width
                height: 40

                MouseArea {
                    id: summaryBoxClicker
                    anchors.fill: parent

                    onClicked: {
                        if(delegateItemThingy.state != "expanded")
                            delegateItemThingy.state = "expanded"
                        else
                            delegateItemThingy.state = "default"
                    }
                }

                Item {
                    id: column1
                    anchors.fill: parent

                    Item {
                        id: summaryBox
                        height: 40
                        anchors.right: parent.right
                        anchors.left: parent.left
                        anchors.top: parent.top
                        Rectangle {
                            id: summaryIcon
                            width: 40
                            height: 40
                            color: colorCode
                            border.color: colorCode
                            gradient: Gradient {
                                GradientStop {
                                    position: 0.00;
                                    color: Qt.darker(colorCode,1.2);
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
                            }
                            Label {
                                id: summarySubLabel
                                text: timest
                            }
                        }
                    }

                    Item {
                        id: detailBox
                        anchors.fill: parent
                        opacity: 0
                        x: 0
                        y: 40
                        anchors.topMargin: 45

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
                                text: has_bin ? "Yes" : "No"
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
                            height: parent.height-40
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
            }
            model: data_source
        }
    }
}
