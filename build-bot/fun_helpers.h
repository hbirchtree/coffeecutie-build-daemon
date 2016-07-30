#pragma once
#include "datastructures.h"

#include <coffee/core/CJSONParser>
#include <coffee/core/CXmlParser>
#include <coffee/core/CProfiling>

cstring buildrep_server = "localhost";
cstring crosscompiling = nullptr;
uint16 buildrep_server_port = 5000;

FORCEDINLINE bool ReportBuildStatus(uint16 status, CString const& commit, CString const& log,uint64 btime)
{
    ProfContext _m("Build reporting");

    REST::Host dest = buildrep_server;
    REST::Request req = {};

    /* Build HTTP request */
    HTTP::InitializeRequest(req);
    req.resource = cStringFormat(
                "/logger/data/{0}",
                (crosscompiling) ? crosscompiling : SysInfo::GetSystemString());
    req.port = buildrep_server_port;
    req.reqtype = "POST";
    req.mimeType = "application/json";
    req.values["Accept"] = "application/json";

    /* We create the JSON payload with string formatting. Bleh. */
    req.payload = cStringFormat(
                "{"
                "\"host\": \"{0}\","
                "\"status\": {1},"
                "\"commit\": \"{2}\","
                "\"log\": \"{3}\","
                "\"build-time\": {4}"
                "}",
                SysInfo::HostName(),status,commit,Base64::encode(log.data(),log.size()),btime);

    Profiler::Profile("Request creation");

    cDebug("Sending status to {0}, resource={1}",dest,req.resource);

    auto res = REST::RestRequest(dest,req);

    Profiler::Profile("Request sending and receiving");

    return res.code == 200;
}

FORCEDINLINE cstring JSGetString(JSON::Value const& v, cstring val)
{
    if(v.HasMember(val)&&v[val].IsString())
        return v[val].GetString();
    return "";
}

FORCEDINLINE GitCommit ParseEntry(XML::Element const* el)
{
    if(!el)
        return {};

    XML::Element const* cts = el->FirstChildElement("updated");
    XML::Element const* cid = el->FirstChildElement("id");

    if(!cts || !cid)
        return {};

    Timestamp ts = Time::ParseTimeStdTime(cts->GetText());
    Regex::Pattern patt = Regex::Compile(".+Commit\\/([0-9a-fA-F]+)");

    auto cap = Regex::Match(patt,cid->GetText(),true);

    if(cap.size() < 2)
        return {};

    return {cap[1].s_match[0],ts};
}

FORCEDINLINE Proc_Cmd GetCommand(JSON::Value const& obj)
{
    Proc_Cmd cmd;

    cmd.program = JSGetString(obj,"program");
    if(obj.HasMember("args")&&obj["args"].IsArray())
    {
        for(JSON::Value const& v : obj["args"].GetArray())
        {
            if(v.IsString())
                cmd.argv.push_back(v.GetString());
        }
    }

    return cmd;
}
