#include <QtDebug>
#include <QtWidgets/QApplication>
#include <QtQml/QQmlApplicationEngine>

int main(int argc, char** argv)
{
    QGuiApplication app(argc,argv);

    QQmlApplicationEngine engine;
    engine.load(QUrl("qrc:/qmldata/BuildView.qml"));

    return app.exec();
}
