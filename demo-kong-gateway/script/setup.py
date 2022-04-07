#/usr/bin/python
# -*- coding: utf-8-*-

import urllib2
import json
import argparse
from urlparse import urlparse

kongHost = "localhost"
kongMngPort = "8001"

kong_admin_url = lambda: "http://" + kongHost + ":" + kongMngPort
kong_service_url = lambda: kong_admin_url() + "/services"
kong_route_url = lambda: kong_admin_url() + "/routes"
kong_consumer_url = lambda: kong_admin_url() + "/consumers"

## APIs resources


def common_plugins():
    return [
        {
            "name": "oauth2",
            "config": {
                "enable_password_grant": True,
                "accept_http_if_already_terminated": True,
                "global_credentials": True
            }
        },
        {"name":"custom-add-access-resource-header"},
        {"name": "custom-rate-limiting"}
    ]


def userApiPlugins():
    return [
        {
            "name": "acl",
            "config": {
                "whitelist": ["userApiFrontApi"]
            }
        },
        {"name": "key-auth"},
        {"name": "custom-user-account-restriction"},
        {"name": "custom-api-key-restriction"}
    ]


def accountUserApiPlugins():
    return [
        {
            "name": "acl",
            "config": {
                "whitelist": ["userApiFrontApi"]
            }
        },
        {"name": "key-auth"},
        {"name": "custom-user-account-restriction"},
        {"name": "custom-api-key-restriction"},
        {"name": "custom-ip-restriction"},
        {"name": "custom-add-api-version-header"}
    ]


def systemApiPlugins():
    return [
        {
            "name": "acl",
            "config": {
                "whitelist": ["accessSysApi"]
            }
        },
        {"name": "key-auth"}
    ]

# root-fallbackのプラグインリスト
def fallbackApiPlugins():
    return [
        {
            "name":"request-termination",
            "config": {
                "status_code": 404,
                "body": "{\n  \"status\" : 404,\n  \"message\" : \"no API found\"\n}"
            }
        }
    ]


services = [
    {
        "name": "user-api-gateway",
        "url": "http://api-gateway:8000/user"
    },
    {
        "name": "sys-api-gateway",
        "url": "http://api-gateway:8000/sys"
    },
    {
        "name": "account-service",
        "url": "http://account-service:8080"
    },
    {
        "name": "spiral-service",
        "url": "http://spiral-service:8080"
    },
    {
        "name": "batch-record-service",
        "url": "http://db-node-service:8080",
        "read_timeout": 115000
    },
    {
        "name": "db-node-service",
        "url": "http://db-node-service:8080",
    },
    {
        "name": "site-service",
        "url": "http://site-service:8080"
    },
    {
        "name": "mail-service",
        "url": "http://mail-service:8080"
    },
    {
        "name": "dns-service",
        "url": "http://dns-service:8080"
    },
    {
        "name": "log-service",
        "url": "http://log-service:8080"
    },
    {
        "name": "file-service",
        "url": "http://file-service:8080"
    },
    {
        "name": "upload-file-service",
        "url": "http://file-service:8080",
        "read_timeout": 600000
    },
    {
        "name": "contents-service",
        "url": "http://contents-service:8085/_sys/testEnvironments"
    },
    {
        "name": "kubenode-healthcheck",
        "url": "http://kubenode-healthcheck:8080"
    },
    {
        "name": "service-healthcheck",
        "url": "http://service-healthcheck:8080"
    },
    {
        "name": "fallback-service",
        "url": "http://_"
    }
]

# proxy_hostは適宜書き換える
routes = [
    # 認証API
    {
        "name": "spiralg.auth",
        "paths": ["/oauth2/token"],
        "service": "account-service"
    },
    # userAPIを集約するAPI
    # account-service.v1.userやaccount-service.v1.dbなどへプロキシする
    {
        "name": "spiralg.userapi",
        "paths": ["/v1"],
        "strip_path": True,
        "service": "user-api-gateway",
        "plugin": common_plugins()
    },
    # Sys routes aggregate
    {
        "name": "spiralg.sysapi",
        "paths": ["/sys/v1"],
        "strip_path": True,
        "service": "sys-api-gateway"
    },

    # account-service user routes
    {
        "name": "userApi.accountService",
        "paths": [
            '/user/profile',
        ],
        "service": "account-service",
        "plugin": userApiPlugins()
    },
    # account-service account-user routes
    {
        "name": "accountUserApi.accountService",
        "paths": [
            '/user/users',
            '/user/account',
            '/user/user/apiKeys',
            '/user/bots',
            '/user/groups',
            '/user/agents',
            '/user/memberships',
            '/user/invitations',
            '/user/ipGroups',
            '/user/ipRestrictionApi',
            '/user/ipRestrictionUi',
            '/user/ipRestrictionBots',
            '/user/usageLimit',
            '/user/apiUsages',
            '/user/usages',
            '/user/notificationMails'
        ],
        "service": "account-service",
        "plugin": accountUserApiPlugins()
    },

    # sys-account-service
    {
        "name": "sysApi.accountService",
        "paths": [
            '/sys/users',
            '/sys/accounts',
            '/sys/mfa',
            '/sys/invitations',
            '/sys/requestLimits',
            '/sys/memberships',
            '/sys/usages',
            '/sys/usageLimit',
            '/sys/apiUsages',
            '/sys/bots',
            '/sys/notificationMails'
        ],
        "service": "account-service",
        "plugin": systemApiPlugins()
    },

    # spiral-service account-user routes
    {
        "name": "accountUserApi.spiralService",
        "paths": [
            '/user/scheduleTriggers',
            '/user/apps',
            '/user/appStats',
            '/user/managedApps',
            '/user/groups/(?<group_id>\\d+)/apps',
            '/user/groups/(?<group_id>\\d+)/managedApps',
            '/user/users/(?<user_id>\\d+)/apps',
            '/user/users/(?<user_id>\\d+)/managedApps',
            '/user/allUsers',
            '/user/allAgents',
            '/user/agents/(?<agent_id>\\d+)/apps',
            '/user/agents/(?<agent_id>\\d+)/managedApps',
            '/user/singleRecordMailActions',
            '/user/fixedMailActions',
            '/user/multiRecordMailActions',
            '/user/mailActionJobs',
            '/user/appFixedMailActions',
            '/user/actions',
            '/user/recordActions',
            '/user/dbs/(?<db>\\d+|@[a-zA-Z0-9_]+\\.[a-zA-Z0-9_]+)/records/searchConditions'
        ],
        "service": "spiral-service",
        "plugin": accountUserApiPlugins()
    },
    # spiral-service account-user routes v1.1
    {
        "name": "accountUserApi.spiralService_v1_1",
        "paths": [
            '/user/apps/(?<app_id>\\d+)/actions/(?<action_id>\\d+)/run',
            '/user/apps/(?<app_id>\\d+)/dbs/(?<db>\\d+|@[a-zA-Z0-9_]+\\.[a-zA-Z0-9_]+)/actions',
            '/user/dependenceOnDb/app',
            '/user/dependenceOnFields/app'
        ],
        "regex_priority": 1,
        "service": "spiral-service",
        "plugin": accountUserApiPlugins()
    },
    # sys-spiral-service
    {
        "name": "sysApi.spiralService",
        "paths": [
            '/sys/apps',
            '/sys/scheduleTriggers',
            '/sys/actions',
            '/sys/mailActions',
            '/sys/users/(?<user_id>\\d+)/apps',
            '/sys/apps/(?<app_id>\\d+)/dbs/(?<db>\\d+|@[a-zA-Z0-9_]+\\.[a-zA-Z0-9_]+)/actions'
        ],
        "service": "spiral-service",
        "plugin": systemApiPlugins()
    },
    # Batch API Route Setting (POST)
    {
        "name": "batchApi.recordService",
        "paths": [
            '/user/dbs/(?<db>\\d+|@[a-zA-Z0-9_]+\\.[a-zA-Z0-9_]+)/records/batchInserts',
            '/user/dbs/(?<db>\\d+|@[a-zA-Z0-9_]+\\.[a-zA-Z0-9_]+)/records/batchInserts/(?<batchInsert_id>\\d+)/cancel',
            '/user/dbs/(?<db>\\d+|@[a-zA-Z0-9_]+\\.[a-zA-Z0-9_]+)/records/batchUpdates'
        ],
        "service": "batch-record-service",
        "methods": ["POST", "GET"],
        "plugin": accountUserApiPlugins()
    },
    # db-node-serviceのユーザAPI
    {
        "name": "userApi.dbNodeService",
        "paths": [
            '/user/apps/(?<app_id>\\d+)/emailLogs/exports',
            '/user/apps/(?<app_id>\\d+)/emailLogs/download',
            '/user/dependenceOnDb/batches',
        ],
        "service": "db-node-service",
        "regex_priority":1,
        "plugin": accountUserApiPlugins()
    },
    {
        "name":"accountUserApi.dbNodeService",
        "paths": [
            '/user/dbs',
            '/user/operationSources',
            '/user/emailErrors',
            '/user/apps/(?<app_id>\\d+)/roles/(?<role_id>\\d+)/dbPermissions',
            '/user/apps/(?<app_id>\\d+)/roles/(?<role_id>\\d+)/screenSetting',
        ],
        "service": "db-node-service",
        "plugin": accountUserApiPlugins()
    },
    # db-node-service API v1.1
    {
        "name":"accountUserApi.dbNodeService_v1_1",
        "paths": [
            '/user/apps/(?<app_id>\\d+)/dbs'
        ],
        "service": "db-node-service",
        "regex_priority": 0,
        "plugin": accountUserApiPlugins()
    },
    # sys db-node-service
    {
        "name": "sysApi.dbNodeService",
        "paths": [
            '/sys/dbNodes',
            '/sys/accountSchemas',
            '/sys/operationSources',
            '/sys/dbs',
            '/sys/emailErrors',
            '/sys/deletedDbs',
            '/sys/apps/(?<app_id>\\d+)/roles/(?<role_id>\\d+)/dbPermissions'
        ],
        "service": "db-node-service",
        "plugin": systemApiPlugins()
    },
    # account user mail-service
    {
        "name": "accountUserApi.mailService",
        "paths": [
            '/user/express/email',
            '/user/emailJobs',
            '/user/dependenceOnDb/emails',
        ],
        "service": "mail-service",
        "plugin": accountUserApiPlugins()
    },
    # account user mail-service v1.1
    {
        "name": "accountUserApi.mailService_v1_1",
        "paths": [
            '/user/apps/(?<app_id>\\d+)/dbs/(?<db>\\d+)/express/email',
            '/user/apps/(?<app_id>\\d+)/dbs/(?<db>\\d+)/emailJobs',
        ],
        "regex_priority": 1,
        "service": "mail-service",
        "plugin": accountUserApiPlugins()
    },
    # sys mail-service
    {
        "name": "sysApi.mailService",
        "paths": [
            '/sys/express/email',
            '/sys/emailJobs'
        ],
        "service": "mail-service",
        "plugin": systemApiPlugins()
    },

    # account user dns-service
    {
        "name": "accountUserApi.dnsService",
        "paths": ["/user/emailFromDomains"],
        "service": "dns-service",
        "plugin": accountUserApiPlugins()
    },
    # sys dns-service
    {
        "name": "sysApi.dnsService",
        "paths": ['/sys/emailFromDomains'],
        "service": "dns-service",
        "plugin": systemApiPlugins()
    },

    # user log-service
    {
        "name": "userApi.logService",
        "paths": [
            '/user/loginHistories',
        ],
        "service": "log-service",
        "regex_priority":0,
        "plugin": userApiPlugins()
    },
    # account-user log-service
    {
        "name": "accountUserApi.logService",
        "paths": [
            '/user/apps/(?<app_id>\\d+)/emailLogs',
            '/user/accessHistories',
            '/user/apps/(?<app_id>\\d+)/clickCountLogs',
            '/user/apps/(?<app_id>\\d+)/openCountLogs',
        ],
        "service": "log-service",
        "regex_priority":0,
        "plugin": accountUserApiPlugins()
    },
    # account-user log-service v1.1
    {
        "name": "accountUserApi.logService_v1_1",
        "paths": [
            '/user/apps/(?<app_id>\\d+)/dbs/(?<db>\\d+)/emailLogs',
        ],
        "regex_priority": 1,
        "service": "log-service",
        "plugin": accountUserApiPlugins()
    },
    # sys log-service
    {
        "name": "sysApi.logService",
        "paths": [
            '/sys/apps/(?<app_id>\\d+)/emailLogs',
            '/sys/loginHistories',
            '/sys/accessHistories'
        ],
        "service": "log-service",
        "plugin": systemApiPlugins()
    },

    # user file-service
    {
        "name": "userApi.fileService",
        "paths": [
            '/user/accounts/(?<account_id>\\d+)/icon',
            '/user/profile/icon',
        ],
        "service": "file-service",
        "plugin": userApiPlugins()
    },
    # account-user file-service
    {
        "name": "accountUserApi.fileService",
        "paths": [
            '/user/account/icon',
            '/user/account/users/(?<user_id>\\d+)/icon',
            '/user/apps/(?<app_id>\\d+)/icon',
            '/user/dbs/(?<db>\\d+|@[a-zA-Z0-9_]+\\.[a-zA-Z0-9_]+)/(?<field>\\d+|@[a-zA-Z0-9_]+)/files',
            '/user/sites/(?<site_id>\\d+)/files'
        ],
        "service": "file-service",
        "plugin": accountUserApiPlugins()
    },
    # account-user file-service v1.1
    {
        "name": "accountUserApi.fileService_v1_1",
        "paths": [
            '/user/apps/(?<app_id>\\d+)/dbs/(?<db>\\d+)/(?<field>\\d+)/files',
            '/user/apps/(?<app_id>\\d+)/dbs/(?<db>\\d+)/(?<field>\\d+)/(?<record>\\d+)/files',
        ],
        "service": "file-service",
        "regex_priority": 1,
        "plugin": accountUserApiPlugins()
    },

    # sys file-service
    {
        "name": "sysApi.fileService",
        "paths": [
            '/sys/dbs/(?<db>\\d+|@[a-zA-Z0-9_]+\\.[a-zA-Z0-9_]+)/(?<field>\\d+|@[a-zA-Z0-9_]+)/files/uploadToken',
            '/sys/dbs/(?<db>\\d+|@[a-zA-Z0-9_]+\\.[a-zA-Z0-9_]+)/(?<field>\\d+|@[a-zA-Z0-9_]+)/files',
            '/sys/users/(?<user_id>\\d+)/icon',
            '/sys/accounts/(?<account_id>\\d+)/icon',
            '/sys/v1/cephCredentials',
            '/sys/sites/(?<site_id>\\d+)/files'
        ],
        "service": "file-service",
        "plugin": systemApiPlugins()
    },
    # file-serviceのユーザAPI (POST Mapping)
    {
        "name": "userApi.uploadFileService",
        "paths": [
            '/user/dbs/(?<db>\\d+|@[a-zA-Z0-9_]+\\.[a-zA-Z0-9_]+)/(?<field>\\d+|@[a-zA-Z0-9_]+)/files'
        ],
        "service": "upload-file-service",
        "methods": ["POST"],
        "plugin": accountUserApiPlugins()
    },

    # contents-service
    {
        "name": "sysApi.contentsService",
        "paths": ["/sys/testEnvironments"],
        "service": "contents-service",
        "strip_path": True,
        "plugin": systemApiPlugins()
    },

    # account user site-service
    {
        "name": "accountUserApi.siteService",
        "paths": [
            '/user/sites',
            '/user/siteStats',
            '/user/allUsers/managedSites',
            '/user/users/(?<id>\\d+)/managedSites',
            '/user/agents/(?<id>\\d+)/managedSites',
            '/user/groups/(?<group_id>\\d+)/managedSites',
            '/user/agents/(?<id>\\d+)/siteApis',
            '/user/groups/(?<group_id>\\d+)/siteApis',
            '/user/dependenceOnDb/sites',
            '/user/dependenceOnFields/sites',
        ],
        "service": "site-service",
        "plugin": accountUserApiPlugins()
    },
    # sys site-service
    {
        "name": "sysApi.siteService",
        "paths": [
            '/sys/deletedSites',
            '/sys/siteEnvironments',
            '/sys/sites',
            '/sys/sites/(?<site_id>\\d+)/originalDomain',
            '/sys/sites/(?<site_id>\\d+)/fileInfo'
        ],
        "service": "site-service",
        "plugin": systemApiPlugins()
    },

    # ヘルスチェック
    {
        "name": "check.kubenode",
        "paths": ["/check/kubenode"],
        "service": "kubenode-healthcheck"
    },
    {
        "name": "check.service",
        "paths": ["/check/service"],
        "service": "service-healthcheck"
    },
    # 上記pathsに該当しないAPI
    {
        "name": "root-fallback",
        "paths": ["/"],
        "service": "fallback-service",
        "plugin": fallbackApiPlugins()
    }
]

consumers = [
    # userapiを集約してuserapi.v1.userなどへプロキシする用のコンシューマー
    {
        "name":"spiralg.userapi",
        "key-auth": {"key":"spiralg.userapi_keyauths_key"},
        "acl":"userApiFrontApi"
    },
    # bff用consumer
    {
        "name":"bff",
        "key-auth": {"key": "bff_keyauths_key"},
        "acl":"accessSysApi"
    },
    # account-service用consumer
    {
        "name":"account-service",
        "key-auth": {"key": "account_service_keyauths_key"},
        "acl":"accessSysApi"
    },
    # email-error-reflector用consumer
    {
        "name":"email-error-reflector",
        "key-auth": {"key": "email_error_reflector_keyauths_key"},
        "acl":"accessSysApi"
    },
    # mail-controller
    {
        "name":"mail-controller",
        "key-auth": {"key": "mail_controller_keyauths_key"},
        "acl":"accessSysApi"
    },
    # mail-agent
    {
        "name":"mail-agent",
        "key-auth": {"key": "mail_agent_keyauths_key"},
        "acl":"accessSysApi"
    },
    # site-service
    {
        "name":"site-service",
        "key-auth": {"key": "site_service_keyauths_key"},
        "acl":"accessSysApi"
    },
    # click-count-service
    {
        "name":"click-count-service",
        "key-auth": {"key": "click_count_service_keyauths_key"},
        "acl":"accessSysApi"
    },
    # contents-service
    {
        "name":"contents-service",
        "key-auth": {"key": "contents_service_keyauths_key"},
        "acl":"accessSysApi"
    },
    # spiral-service consumer
    {
        "name":"spiral-service",
        "key-auth": {"key": "spiral_service_keyauths_key"},
        "acl":"redirectRadosgw"
    },
    # log-service consumer
    {
        "name":"log-service",
        "key-auth": {"key": "log_service_keyauths_key"},
        "acl":"accessSysApi"
    },
    # mail-service consumer
    {
        "name":"mail-service",
        "key-auth": {"key": "mail_service_keyauths_key"},
        "acl":"accessSysApi"
    },
    # db-node-batch-service consumer
    {
        "name":"db-node-batch-service",
        "key-auth": {"key": "db_node_batch_service_keyauths_key"},
        "acl":"accessSysApi"
    },
    # db-node-service consumer
    {
        "name":"db-node-service",
        "key-auth": {"key": "db_node_service_keyauths_key"},
        "acl":"accessSysApi"
    },
    # file-service consumer
    {
        "name":"file-service",
        "key-auth": {"key": "file_service_keyauths_key"},
        "acl":"accessSysApi"
    }
]


## Kong resource functions


def get_kong_resource(url):
    try:
        r = urllib2.urlopen(url)
        s_res = json.loads(r.read())
        return s_res
    except urllib2.HTTPError as e:
        if e.code == 404:
            return None
        else:
            raise e


def create_kong_resource(url, params):
    req = urllib2.Request(url, params)
    req.add_header('Content-Type', 'application/json')
    try:
        res = urllib2.urlopen(req)
        return json.loads(res.read())
    except urllib2.HTTPError as e:
        print params
        print 'failed to create resource "{}"'.format(url)
        print e.message


def update_kong_resource(url, params):
    req = urllib2.Request(url, params)
    req.add_header('Content-Type', 'application/json')
    req.get_method = lambda: 'PATCH'
    try:
        res = urllib2.urlopen(req)
        return json.loads(res.read())
    except urllib2.HTTPError as e:
        print params
        print 'failed to update resource "{}"'.format(url)
        print e.message


def delete_kong_resource(url):
    req = urllib2.Request(url)
    req.get_method = lambda: 'DELETE'
    urllib2.urlopen(req)


## Kong sevice functions

def add_services():
    for service in services:
        retries = service["retries"] if "retries" in service else 0
        params = {
            "name": service["name"],
            "url": service["url"],
            "retries": retries
        }
        if "read_timeout" in service:
            params["read_timeout"] = service["read_timeout"]

        json_params = json.dumps(params)
        if service_exists(service["name"]):
            url = kong_service_url() + "/" + service["name"]
            update_kong_resource(url, json_params)
        else:
            create_kong_resource(kong_service_url(), json_params)


def service_exists(name):
    url = kong_service_url() + "/" + name
    return get_kong_resource(url) is not None


def delete_services(services):
    for service in services:
        service_url = kong_service_url() + "/" + service["name"]
        delete_kong_resource(service_url)


## Kong route functions


def add_routes():
    for route in routes:
        strip_path = route['strip_path'] if 'strip_path' in route else False
        regex_priority = route['regex_priority'] if 'regex_priority' in route else 0
        params = {
            "name": route["name"],
            "paths": route["paths"],
            "strip_path": strip_path,
            "regex_priority":regex_priority
        }
        if 'methods' in route:
            params["methods"] = route["methods"]

        json_params = json.dumps(params)

        if route_exists(route["name"]):
            update_route(route["name"], json_params)
        else:
            create_route(route["service"], json_params)


def route_exists(name):
    url = kong_route_url() + "/" + name
    return get_kong_resource(url) is not None


def create_route(service, params):
    url = kong_service_url() + "/" + service + "/routes"
    return create_kong_resource(url, params)


def update_route(route_name, params):
    url = kong_route_url() + "/" + route_name
    return update_kong_resource(url, params)


def delete_routes():
    for api in routes:
        route_url = kong_route_url() + "/" + api["name"]
        delete_kong_resource(route_url)


## Kong plugin functions


def add_plugins():
    for route in routes:
        if not route_exists(route["name"]):
            print 'Add plugins fail, route not exists: ' + route["name"]
            continue

        plugins = route["plugin"] if 'plugin' in route else []
        for plugin in plugins:
            plugin_id = get_plugin_id(route["name"], plugin["name"])
            configs = plugin["config"] if 'config' in plugin else {}
            params = {"name": plugin["name"], "config": configs}
            if plugin_id is None:
                params_str = json.dumps(params)
                create_plugin(route["name"], params_str)
            else:
                update_plugin(plugin_id, params)


def plugin_exists(route_name, plugin_name):
    url = kong_route_url() + "/" + route_name + "/plugins/"
    res = get_kong_resource(url)
    return any(p["name"] == plugin_name for p in res["data"])


def get_plugin_id(route_name, plugin_name):
    url = kong_route_url() + "/" + route_name + "/plugins/"
    res = get_kong_resource(url)
    for plugin in res["data"]:
        if plugin_name == plugin["name"]:
            return plugin["id"]
    return None


def create_plugin(route_name, params):
    url = kong_route_url() + "/" + route_name + "/plugins/"
    return create_kong_resource(url, params)


def update_plugin(plugin_id, params):
    url = kong_admin_url() + "/plugins/" + plugin_id
    res = get_kong_resource(url)
    res["name"] = params["name"]
    for key in params["config"].keys():
        res["config"][key] = params["config"][key]
    return update_kong_resource(url, json.dumps(res))


## Kong consumer functions


def consumer_exists(name):
    url = kong_consumer_url() + "/" + name
    return get_kong_resource(url) is not None


def add_consumer_key(consumer_name, authen_name, params):
    if not exists_authentication(consumer_name, authen_name):
        url = kong_consumer_url() + "/" + consumer_name + "/" + authen_name
        create_kong_resource(url, params)


def add_consumers(is_production):
    for consumer in consumers:
        if not consumer_exists(consumer["name"]):
            params = json.dumps({"username": consumer["name"]})
            create_kong_resource(kong_consumer_url(), params)

        if ("oauth2" in consumer):
            params = json.dumps(consumer["oauth2"])
            add_consumer_key(consumer["name"], "oath2", params)

        if ("key-auth" in consumer
                and not exists_authentication(consumer["name"], "key-auth")):
            url = kong_consumer_url() + "/" + consumer["name"] + "/key-auth"
            if is_production:
                urllib2.Request(url, '')
            else:
                params = json.dumps(consumer["key-auth"])
                create_kong_resource(url, params)

        if ("acl" in consumer):
            params = json.dumps({"group": consumer["acl"]})
            add_consumer_key(consumer["name"], "acls", params)


def exists_authentication(consumer_name, authen_name):
    url = kong_consumer_url() + "/" + consumer_name + "/" + authen_name
    res = get_kong_resource(url)
    return len(res["data"]) > 0


## App functions


#
# request-transformerプラグインをを登録
#
def addRequestTransformer(_name):
    if plugin_exists(_name, "request-transformer"):
        return

    url = kong_consumer_url() + '/' + _name + '/key-auth'
    res = json.loads(urllib2.urlopen(url).read())['data']

    if len(res) == 0:
        print 'failed to add request-transformer plugin: ' + _name
        return

    keyauth_key = res[0]['key']
    plugin = {
        'name': 'request-transformer',
        'config': {
            'add': {
                'headers': ['apikey:{}'.format(keyauth_key)]
            }
        }
    }
    params = json.dumps(plugin)
    create_plugin(_name, params)


def delete_all_consumers():
    for consumer in consumers:
        req = urllib2.Request(kong_consumer_url() + "/" + consumer['name'])
        req.get_method = lambda: 'DELETE'
        try:
            urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            if e.code == 404:
                print 'INFO: {} consumer is not found.'.format(
                    consumer['name'])
            else:
                raise e


def delete_all_service_and_routes():
    delete_routes()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host',
        action='store',
        default=kongHost,
        help='Kong Admin API host or IP')
    parser.add_argument(
        '--port',
        action='store',
        default=kongMngPort,
        help='Kong Admin API port')
    parser.add_argument(
        '--delete-consumer',
        action='store_true',
        help='delete all consumer definitions')
    parser.add_argument(
        '--delete-service-route',
        action='store_true',
        help='delete all Service/Route definitions')
    parser.add_argument(
        '--production',
        action='store_true',
        default=False,
        help='for Production (and Staging) environment')
    args = parser.parse_args()
    kongHost = args.host
    kongMngPort = args.port

    if args.delete_consumer:
        delete_all_consumers()

    if args.delete_service_route:
        delete_all_service_and_routes()

    add_services()
    add_routes()
    add_plugins()
    add_consumers(args.production)
    addRequestTransformer("spiralg.userapi")
