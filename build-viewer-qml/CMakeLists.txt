include ( QtIncludes )

add_definitions ( -DUSE_COFFEE_MAIN )

include_directories ( include )

qt5_add_resources ( RESOURCES qml_source.qrc )
qt5_wrap_cpp ( Viewer_Headers include/buildfetcher.h )

set ( Viewer_Srcs
    main.cpp

    ${Viewer_Headers}
    ${RESOURCES}
    )

coffee_add_example ( BuildViewer "Build Viewer" "${Viewer_Srcs}" CoffeeCore )

qt5_use_modules ( BuildViewer Widgets Quick Network )
