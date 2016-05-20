import QtQuick 2.4
import QtQuick.Controls 1.4

Item {
    property alias loadIndicatorWidget: loadIndicate;
    property alias listView: listView;

    id: item1
    width: 400
    height: 400

    ListView {
        id: listView
        boundsBehavior: Flickable.DragOverBounds
        anchors.rightMargin: 5
        anchors.leftMargin: 5
        anchors.fill: parent
        spacing: 5
    }

    BusyIndicator {
        id: loadIndicate
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        visible: false
        running: false
    }
}
