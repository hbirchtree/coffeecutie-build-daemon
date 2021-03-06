TEMPLATE = app

QT += qml quick widgets

CONFIG += c++11 qtquickcompiler

INCLUDEPATH += include

SOURCES += main.cpp
HEADERS += include/buildfetcher.h
RESOURCES += qml_source.qrc

# Additional import path used to resolve QML modules in Qt Creator's code model
QML_IMPORT_PATH = qml

# Default rules for deployment.
include(BuildViewerDeploy.pri)

DISTFILES += \
    android/AndroidManifest.xml \
    android/gradle/wrapper/gradle-wrapper.jar \
    android/gradlew \
    android/res/values/libs.xml \
    android/build.gradle \
    android/gradle/wrapper/gradle-wrapper.properties \
    android/gradlew.bat

ANDROID_PACKAGE_SOURCE_DIR = $$PWD/android
