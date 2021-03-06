import QtQuick 2.4
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.1
import QtQuick.Window 2.0
import BuildView 1.0
import "."

ApplicationWindow {
    width: 640
    height: 480

    function max(a, b)
    {
        return a > b ? a : b;
    }

    id: app
    color: GlobalData.backgroundBase

    title: qsTr("Build Viewer")
    visible: true
    onSceneGraphInitialized: {
        console.log("Scaling factor: "+GlobalData.scalingCoeff)
    }

    BuildInfo {
        id: data_source
        server: logform.connectHost
        serverPort: logform.connectPort
        onFetchingChanged: {
            bform.loadIndicatorWidget.running = data_source.fetching
            bform.loadIndicatorWidget.visible = data_source.fetching
        }
    }

    BuildViewForm {
        id: bform
        anchors.fill: parent

        loadIndicatorWidget.running: data_source.fetching
        loadIndicatorWidget.visible: data_source.fetching

        listView.delegate: BuildItem {
            width: parent.width
            onItemPressed: {
                details.platform = platform;
                details.host = host;
                details.commit = commit;
                details.status = status;
                details.build_id = bid;
                details.timestamp = timest;
                details.has_binary = has_bin;

                details.toggleShow()
            }
        }
        listView.model: data_source
    }

    DetailsPopup{
        id: details
        focus: true

        width: parent.width
        height: parent.height

        onBackgroundTouched: toggleShow()

        coverage: {
            parent.width < 800
                    ? 0.8 :
                      320*GlobalData.scalingCoeff/parent.width;
        }

        onDownloadPressed: Qt.openUrlExternally(
                               "http://"+data_source.server
                               +":"+data_source.serverPort+"/bin/"+build_id)

        onViewLogPressed: Qt.openUrlExternally(
                              "http://"+data_source.server
                              +":"+data_source.serverPort+"/logs/"+build_id)
    }

    LoginForm{
        id: logform
        width: parent.width
        height: parent.height
        state: "compact"

        onConnectPressed: {
            data_source.server = connectHost
            data_source.serverPort = connectPort
            state = "default"
            data_source.update()
        }
    }
}
