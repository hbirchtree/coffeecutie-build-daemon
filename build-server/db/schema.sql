CREATE TABLE BUILDREPORTS(
    REPORT_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    SERVERID TEXT[60] NOT NULL,
    BUILD_HASH TEXT[60] NOT NULL,
    PLATFORM_ID TEXT[60] NOT NULL,
    BUILD_STATUS INTEGER,
    ERROR_OUTPUT BLOB,
    BUILD_TIME DATETIME NOT NULL,
    HAS_BINARY INTEGER NOT NULL
);

CREATE TEST_BUILDREL(
    REPORT_ID INTEGER PRIMARY KEY NOT NULL,
    TEST_ID INTEGER PRIMARY KEY NOT NULL
);

CREATE TABLE TEST_REPORT(
    TEST_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    RESULT INTEGER NOT NULL,
    BTIME DATETIME NOT NULL
);

CREATE TABLE UNIT_TESTREL(
    TEST_ID INTEGER PRIMARY KEY NOT NULL,
    UNIT_ID INTEGER PRIMARY KEY NOT NULL
);

CREATE TABLE UNIT_TEST(
    UNIT_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    RESULT INTEGER NOT NULL,
    UNAME TEXT[60] NOT NULL
);
