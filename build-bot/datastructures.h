#pragma once

#include <coffee/CAsio>
#include <coffee/core/CMD>

using namespace Coffee;

enum FailureCase
{
    Nothing,

    NoRepoSpecified = 20,
    FeedFetchFailed = 21,

    ProcessFailed   = 22,
    XMLParseFailed  = 23,
};

enum UpdateSource
{
    GithubRSS = 1,
};

enum BuildTypes
{
    CMakeSystem = 1,
};

enum BuildSpecs
{
    IgnoreFailure = 0x1,
    CleanAlways   = 0x2,
};

struct GitCommit
{
    CString hash;
    Timestamp ts;
};

bool operator<(GitCommit const& c1, GitCommit const& c2)
{
    return c1.ts < c2.ts && c1.hash != c2.hash;
}

struct BuildServer
{
    CString addr;
    uint16 port;
};

struct RepoConfig
{
    CString repository;
    CString branch;
    CString upstream;
};

struct BuildConfig
{
    Vector<Proc_Cmd> queue;

    CString build;
    CString repodir;

    CString system;
    uint64 interval;
};

struct BuildEnvironment
{
    BuildServer server;
    BuildConfig b_cfg;
    RepoConfig r_cfg;
    uint32 flags;
};

struct Repository_tmp
{
    REST::Request request;
    REST::RestResponse response;
    CString expect_type;

    GitCommit last_commit;

    Timestamp wakeup;
};

struct DataSet
{
    BuildEnvironment repo;
    Repository_tmp temp;
};
