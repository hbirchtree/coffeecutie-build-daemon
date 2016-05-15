include ( QtIncludes )

qt5_add_resources ( RESOURCES qml_source.qrc )

set ( Viewer_Srcs
    main.cpp

    ${RESOURCES}
    )

coffee_add_example ( BuildViewer "Build Viewer" "${Viewer_Srcs}" "" )

qt5_use_modules ( BuildViewer Widgets Quick Network )
