include ( QtIncludes )

qt5_add_resources ( RESOURCES qml_source.qrc )
qt5_wrap_cpp ( Viewer_Headers buildfetcher.h )

set ( Viewer_Srcs
    main.cpp

    ${Viewer_Headers}
    ${RESOURCES}
    )

coffee_add_example ( BuildViewer "Build Viewer" "${Viewer_Srcs}" CoffeeCore )

qt5_use_modules ( BuildViewer Widgets Quick Network )
