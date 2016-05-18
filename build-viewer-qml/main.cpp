#include <coffee/core/CApplication>

#include <QtDebug>
#include <QApplication>
#include <QQmlApplicationEngine>
#include <QtQml>

#include "buildfetcher.h"

using namespace Coffee;

int32 qt_main(int32 argc, cstring_w* argv)
{
    QGuiApplication app(argc,argv);

    qmlRegisterType<BuildInformationFetcher>("BuildView",1,0,"BuildInfo");

    QQmlApplicationEngine engine;
    engine.load(QUrl("qrc:/qmldata/BuildView.qml"));

    return app.exec();
}

COFFEE_APPLICATION_MAIN(qt_main)
