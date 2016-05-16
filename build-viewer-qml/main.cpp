#include <QtDebug>
#include <QApplication>
#include <QQmlApplicationEngine>
#include <QtQml>

#include "buildfetcher.h"

int main(int argc, char** argv)
{
    QGuiApplication app(argc,argv);

    qmlRegisterType<BuildInformationFetcher>("buildview",1,0,"BuildInfo");

    QQmlApplicationEngine engine;
    engine.load(QUrl("qrc:/qmldata/BuildView.qml"));

    return app.exec();
}
