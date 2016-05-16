import QtQuick 2.4
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.2

Item {
    property alias loadIndicatorWidget: loadIndicate;

    id: item1
    width: 400
    height: 400

    BusyIndicator {
        id: loadIndicate
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
    }
}
