#ifdef USE_COFFEE_MAIN
#include <coffee/core/CApplication>
#endif

#include <QtDebug>
#include <QApplication>
#include <QQmlApplicationEngine>
#include <QtQml>
#include <QScreen>

#include "buildfetcher.h"

#ifdef USE_COFFEE_MAIN
using namespace Coffee;

int32 qt_main(int32 argc, cstring_w* argv)
#else
int main(int argc, char** argv)
#endif
{
    QGuiApplication app(argc,argv);

    qmlRegisterType<BuildInformationFetcher>("BuildView",1,0,"BuildInfo");

    QQmlApplicationEngine engine;
    engine.load(QUrl("qrc:/BuildView.qml"));

    engine.rootContext()->setContextProperty(
                "scalingCoeff",
                (QGuiApplication::primaryScreen()->physicalDotsPerInch()
                * QGuiApplication::primaryScreen()->devicePixelRatio()) / 120.0);

    return app.exec();
}

#ifdef USE_COFFEE_MAIN
COFFEE_APPLICATION_MAIN(qt_main)
#endif
