#include <coffee/core/CApplication>
#include <coffee/core/CDebug>
#include <coffee/core/CArgParser>

#include "fun_helpers.h"

cstring git_program = "git";
cstring cmake_program = "cmake";

DataSet create_item(cstring file)
{
    /* Clear all structures */
    DataSet repo = {};

    BuildEnvironment& repo_data = repo.repo;

    repo.temp = {};
    repo.temp.last_commit = {};

    /* Default, sane values */
    repo_data.r_cfg.branch = "master";
    repo_data.r_cfg.upstream = "origin";
    repo_data.b_cfg.interval = 3600;
    repo_data.b_cfg.repodir = Env::CurrentDir();
    repo_data.b_cfg.build = Env::CurrentDir();
    CString build_sys = "cmake";

    JSON::Document doc;

    /* Open source file */
    {
        CResources::Resource resc(file);
        CResources::FileMap(resc);

        /* If file not found, no source to add */
        if(!resc.data)
            return {};

        /* Copy data string */
        {
            CString data_string;
            data_string.insert(0,(cstring)resc.data,resc.size);

            CResources::FileUnmap(resc);

            /* Open JSON document from file, it contains all the information */
            doc = JSON::Read(data_string.c_str());
        }

        if(!doc.IsObject())
            return {};
    }

    /* Extract root object and get the data */
    {
        JSON::Value doc_ = doc.GetObject();

        /* Various flags */
        if(doc_.HasMember("cleans")&&doc_["cleans"].GetBool())
            repo_data.flags |= CleanAlways;
        if(doc_.HasMember("nofail")&&doc_["nofail"].GetBool())
            repo_data.flags |= IgnoreFailure;

        /* Server information */
        repo_data.server.addr = JSGetString(doc_,"server:address");
        if(doc_.HasMember("server:port")&&doc_["server:port"].IsUint())
            repo_data.server.port = doc_["server:port"].GetUint();

        /* Repository information */
        repo_data.r_cfg.repository = JSGetString(doc_,"repository");
        repo_data.r_cfg.upstream = JSGetString(doc_,"upstream");
        repo_data.r_cfg.branch = JSGetString(doc_,"branch");

        /* Filesystem locations */
        repo_data.b_cfg.repodir = JSGetString(doc_,"repo-dir");
        repo_data.b_cfg.build = JSGetString(doc_,"build-dir");

        /* Build information */
        build_sys = JSGetString(doc_,"build-type");
        repo_data.b_cfg.system = JSGetString(doc_,"target");

        /* Update rate */
        if(doc_.HasMember("interval"))
            repo_data.b_cfg.interval = doc_["interval"].GetUint64();
    }

    /* Create a list of commands based on build system preference */
    Vector<Proc_Cmd>& cmd_queue = repo_data.b_cfg.queue;

    if(build_sys == "cmake")
    {
        cstring upstream = repo_data.r_cfg.upstream.c_str();
        cstring branch = repo_data.r_cfg.branch.c_str();
        cstring build_dir = repo_data.b_cfg.build.c_str();
        cstring repo_dir = repo_data.b_cfg.repodir.c_str();

        cmd_queue.push_back({git_program,{"-C",repo_dir,"pull",upstream,branch},{}});
        if((repo_data.flags&CleanAlways))
            cmd_queue.push_back({cmake_program,{"--build",build_dir,"--target","clean"},{}});
        cmd_queue.push_back({cmake_program,{"--build",build_dir,"--target","install"},{}});
    }else{
        cWarning("Unrecognized build system: {0}",build_sys);
    }

    /* Create stream and MIME-type preferences */
    repo.temp.expect_type = "application/atom+xml; charset=utf-8";

    REST::Request& request = repo.temp.request;
    {
        HTTP::InitializeRequest(request);
        request.transp = REST::HTTPS;
        request.values["Accept"] = "application/atom+xml";
        request.resource = cStringFormat("/{0}/commits/{1}.atom",
                                         repo_data.r_cfg.repository,
                                         repo_data.r_cfg.branch);
    }

    /* Print preferences back to user */
    cBasicPrint("\nConfigured target:\n"
                "repository = {0}\n"
                "branch = {5}\n"
                "upstream = {6}\n"
                "repository-dir = {1}\n"
                "build-dir = {2}\n"
                "interval = {3}\n"
                "build-system = {4}\n"
                "build-flags = {7}\n",
                repo_data.r_cfg.repository,
                repo_data.b_cfg.repodir,
                repo_data.b_cfg.build,
                repo_data.b_cfg.interval,
                build_sys,
                repo_data.r_cfg.branch,
                repo_data.r_cfg.upstream,
                repo_data.flags);

    return repo;
}

FailureCase update_item(BuildEnvironment const& data, Repository_tmp* workarea)
{
    /* If it is not our time, don't do anything */
    if(Time::CurrentTimestamp() < workarea->wakeup)
        return Nothing;

    /* Set global variables for server and system configuration */
    if(!data.b_cfg.system.empty())
        crosscompiling = data.b_cfg.system.c_str();
    else
        crosscompiling = nullptr;

    buildrep_server = data.server.addr.c_str();
    buildrep_server_port = data.server.port;

    /* References for faster typing */
    uint64 const& interval = data.b_cfg.interval;
    REST::Request const& request = workarea->request;
    CString const& expect_type = workarea->expect_type;
    CString const& repo = data.r_cfg.repository;
    Vector<Proc_Cmd> const command_queue = data.b_cfg.queue;

    cBasicPrint("WORKING ON: {0}",repo);

    /* Make a request for the latest commits */
    auto response = REST::RestRequest("github.com",request);

    /* If not successful, fail and die */
    if(response.code != 200 && !(data.flags&IgnoreFailure))
        return FeedFetchFailed;

    /* Only proceed if MIME-type is correct */
    if(REST::GetContentType(response) == expect_type)
    {
        /* Extract Atom feed and find latest commit (first in list, hopefully) */
        XML::Document* doc = XML::XMLRead(
                    BytesConst{response.payload.size(),(byte_t*)response.payload.c_str()});

        XML::Element* feed = doc->FirstChildElement("feed");

        /* If failed to get first feed, die */
        if(!feed)
        {
            if(!(data.flags&IgnoreFailure))
                return XMLParseFailed;
        }else{
            /* Get information on latest commit in simple format */
            GitCommit cmt = ParseEntry(feed->FirstChildElement("entry"));

            /* If this new commit is later than our current, go ahead and build */
            if(workarea->last_commit < cmt)
            {
                workarea->last_commit = cmt;

                cBasicPrint("Updated repository: {0}, commit={1}, ts={2}",
                            repo,cmt.hash,cmt.ts);

                /* Execute command queue, die if error */
                uint16 signal = 0;
                CString log;

                uint64 timer = Time::CurrentMicroTimestamp();

                for (Proc_Cmd const& cmd : command_queue)
                {
                    cBasicPrintNoNL("Running: {0}",cmd.program);
                    for(CString const& a : cmd.argv)
                        cBasicPrintNoNL(" {0}",a);
                    cBasicPrintNoNL("\n");
                    /* Execute command, capturing log and signal */
                    int sig = Proc::ExecuteLogged(cmd, &log);
                    if (sig != 0)
                    {
                        /* On failure, either submit with error or return */
                        signal = 1;
                        cBasicPrint("Failed with signal {0}:\n{1}", sig, log);
                        if(!(data.flags&IgnoreFailure))
                            return ProcessFailed;
                        break;
                    }
                }

                /* Send build report */
                ReportBuildStatus(signal,cmt.hash,log,Time::CurrentMicroTimestamp()-timer);
            }else{
                cWarning("Mismatch commit, latest is commit={0}, ts={1}",
                         workarea->last_commit.hash,workarea->last_commit.ts);
            }
        }
        delete doc;
    }else{
        cWarning("Content mismatch: \"{0}\", expected \"{1}\"",
                 REST::GetContentType(response),
                 expect_type);
        return XMLParseFailed;
    }

    /* Find out when to wake up next time */
    workarea->wakeup = Time::CurrentTimestamp()+interval;

    cBasicPrint("Sleeping again, waking up at {0}",
                Time::LocalTimeString(workarea->wakeup));

    cBasicPrint("");

    return Nothing;
}

int32 coffee_main(int32 argc, cstring_w* argv)
{
    Vector<DataSet> datasets;

    {
        ArgumentCollection args;

        /* Allow customizing path to Git and CMake, for Windows */
        args.registerArgument(ArgumentCollection::Argument,"help");
        args.registerArgument(ArgumentCollection::Argument,"gitbin");
        args.registerArgument(ArgumentCollection::Argument,"cmakebin");

        args.parseArguments(argc,argv);

        for(std::pair<CString,cstring> const& arg : args.getArgumentOptions())
        {
            if(arg.first == "help" && arg.second)
            {
                cBasicPrint("{0} [options] {configs (.json)}\n"
                            "Options available:\n"
                            " --help Show this message and exit\n"
                            " --gitbin [bin] Specify Git binary\n"
                            " --cmakebin [bin] Specify CMake binary\n",
                            Env::ExecutableName());
                return 0;
            }
            else if(arg.first == "gitbin" && arg.second)
                git_program = arg.second;
            else if(arg.first == "cmakebin" && arg.second)
                cmake_program = arg.second;
        }

        /* All positional arguments are interpreted as file paths */
        for(cstring it : args.getPositionalArguments())
        {
            datasets.push_back(create_item(it));
        }
    }

    /* Will not enter loop if no work items are found */
    if(datasets.size() == 0)
        return 0;

    cDebug("Got {0} datasets\n",datasets.size());

    /* Start the REST service */
    REST::InitService();

    cDebug("Launched BuildBot");

    /* Initiate blast processing, watch processor burn */
    while(true)
    {
        for(DataSet& e : datasets)
        {
            int sig = update_item(e.repo, &e.temp);
            if (sig != Nothing)
                return sig;
        }
        Threads::sleepMillis(250);
    }
}

COFFEE_APPLICATION_MAIN(coffee_main);
