#
# Copyright 2022 DIGITAL.AI
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import traceback
import sets
import sys
import urllib
import json
import base64
from xlrelease.HttpRequest import HttpRequest
import logging
import requests
import re

logger = logging.getLogger(__name__)

HTTP_SUCCESS = sets.Set([200, 201, 202, 203, 204, 205, 206, 207, 208])
HTTP_ERROR = sets.Set([400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410,412, 413, 414, 415])

class Mabl_Client(object):
    def __init__(self, httpConnection, token=None, tokenCICD=None, failTaskOnFailedTest=True):
        self.httpConnection = httpConnection
        self.workspaceId = httpConnection['workspaceId']
        self.token = token
        if token is None:
            self.token = httpConnection['token']
        self.tokenCICD = tokenCICD
        if tokenCICD is None:
            self.tokenCICD = httpConnection['tokenCICD']
        self.failTaskOnFailedTest = failTaskOnFailedTest
        self.httpRequest = HttpRequest(httpConnection)


    @staticmethod
    def create_client(httpConnection, token=None, tokenCICD=None, failTaskOnFailedTest=True):
        return Mabl_Client(httpConnection, token, tokenCICD, failTaskOnFailedTest)


    def testServer(self):
        api_key_bytes = self.token.encode('ascii')
        Base64String = base64.b64encode(api_key_bytes)
        Base64String = "Basic %s" % Base64String
        logger.debug("testServer: Base64String %s" % Base64String)

        headers = {
          "Content-Type": "application/json",
          "Authorization": Base64String
        }

        response = self.httpRequest.get("login", headers=headers)
        

    def mabl_runtest(self, variables):
        api_key_bytes = self.token.encode('ascii')
        Base64String = base64.b64encode(api_key_bytes)
        Base64String = "Basic %s" % Base64String

        headers = {
          "Content-Type": "application/json",
          "Authorization": Base64String
        }

        payload =   {}
        
        if len(variables['environmentId']) > 0:
            env = {"environment_id": self.parseEnv(variables['environmentId'])}
            payload.update(env)
        if len(variables['applicationId']) > 0:
            app = {"application_id": self.parseApp(variables['applicationId'])}
            payload.update(app)
        if len(variables['planLabels']) > 0:
            plans = {"plan_labels": variables['planLabels']}
            payload.update(plans)

        mablUrl = "events/deployment"
        logger.debug("Test Run URL %s" % mablUrl)
        logger.debug("\nPayload==========\n%s\n===============" % json.dumps(payload, indent=4, sort_keys=True))

        response = self.httpRequest.post(mablUrl, json.dumps(payload), headers=headers)
        data = json.loads(response.getResponse())
        logger.debug("Start Test Response\n=============\n%s\n==================" % json.dumps(response.getResponse(), indent=4, sort_keys=True))

        if response.getStatus() not in HTTP_SUCCESS:
            logger.error("Start Test Request Error (%s)" % str(response.getStatus()))
            self.throw_error(response)
        data = json.loads(response.getResponse())
        return data['id']

    def parseEnv(self, envString):
        regex = r"[a-zA-Z0-9]*-e"
        if re.search(regex, envString):
            return re.search(regex, envString).group()
        else:
            raise Exception("The entered string - %s - does not contain an environment id. Expected pattern is alpha-numeric followed by -e." % envString)

    def parseApp(self, appString):
        regex = r"[a-zA-Z0-9]*-a"
        if re.search(regex, appString):
            return re.search(regex, appString).group()
        else:
            raise Exception("The entered string - %s - does not contain an application id. Expected pattern is alpha-numeric followed by -a." % appString)



    def mabl_waitfortest(self, variables):
        api_key_bytes = self.token.encode('ascii')
        Base64String = base64.b64encode(api_key_bytes)
        Base64String = "Basic %s" % Base64String

        headers = {
          "Content-Type": "application/json",
          "Authorization": Base64String
        }

        mablUrl = "execution/result/event/%s" % variables['testId']
        logger.debug("Wait for Test URL %s" % mablUrl)
        response = self.httpRequest.get(mablUrl, headers=headers, contentType='application/json')
        data = json.loads(response.getResponse())
        logger.debug("Start Test Response\n=============\n%s\n==================" % json.dumps(data, indent=4, sort_keys=True))

        if response.getStatus() not in HTTP_SUCCESS:
            logger.error("Wait for Test Request Error (%s)" % response.getStatus())
            self.throw_error(response)

        data = json.loads(response.getResponse())
        data['output'] = {}
        data['output']['journeyExecutionFailed'] = data['journey_execution_metrics']['failed']
        data['output']['journeyExecutionPassed'] = data['journey_execution_metrics']['passed']
        data['output']['journeyExecutionRunning'] = data['journey_execution_metrics']['running']
        data['output']['journeyExecutionSkipped'] = data['journey_execution_metrics']['skipped']
        data['output']['journeyExecutionTerminated'] = data['journey_execution_metrics']['terminated']
        data['output']['journeyExecutionTotal'] = data['plan_execution_metrics']['total']
        data['output']['planExecutionFailed'] = data['plan_execution_metrics']['failed']
        data['output']['planExecutionPassed'] = data['plan_execution_metrics']['passed']
        data['output']['planExecutionTotal'] = data['plan_execution_metrics']['total']

        journeyUrls = []
        for execution in data['executions']:
            for journey in execution['journey_executions']:
                journeyUrls.append(journey['app_href'])
        data['output']['journeyUrl'] = journeyUrls
        return data

    def mabl_getEnvironments(self, variables):
        api_key_bytes = self.tokenCICD.encode('ascii')
        Base64String = base64.b64encode(api_key_bytes)
        Base64String = "Basic %s" % Base64String

        headers = {
          "Content-Type": "application/json",
          "Authorization": Base64String
        }

        mablUrl = "environments?organization_id=%s" % self.workspaceId
        logger.debug("Requesting Environments %s" % mablUrl)
        response = self.httpRequest.get(mablUrl, headers=headers, contentType='application/json')
        data = json.loads(response.getResponse())
        logger.debug("Get Environments Response\n=============\n%s\n==================" % json.dumps(data, indent=4, sort_keys=True))

        if response.getStatus() not in HTTP_SUCCESS:
            logger.error("Get Environments Request Error (%s)" % response.getStatus())
            self.throw_error(response)

        data = json.loads(response.getResponse())
        environmentIds = []
        for env in data['environments']:
            environmentIds.append("%s (%s)" % (env["id"], env["name"]))
        return environmentIds

    def mabl_getApplications(self, variables):
        api_key_bytes = self.tokenCICD.encode('ascii')
        Base64String = base64.b64encode(api_key_bytes)
        Base64String = "Basic %s" % Base64String

        headers = {
          "Content-Type": "application/json",
          "Authorization": Base64String
        }

        mablUrl = "applications?organization_id=%s" % self.workspaceId
        logger.debug("Requesting Applications %s" % mablUrl)
        response = self.httpRequest.get(mablUrl, headers=headers, contentType='application/json')
        data = json.loads(response.getResponse())
        logger.debug("Get Environments Response\n=============\n%s\n==================" % json.dumps(data, indent=4, sort_keys=True))

        if response.getStatus() not in HTTP_SUCCESS:
            logger.error("Get Applications Request Error (%s)" % response.getStatus())
            self.throw_error(response)

        data = json.loads(response.getResponse())
        applicationIds = []
        for app in data['applications']:
            applicationIds.append("%s (%s)" % (app["id"], app["name"]))
        return applicationIds

    def mabl_getLabels(self, variables):
        api_key_bytes = self.tokenCICD.encode('ascii')
        Base64String = base64.b64encode(api_key_bytes)
        Base64String = "Basic %s" % Base64String

        headers = {
          "Content-Type": "application/json",
          "Authorization": Base64String
        }

        mablUrl = "schedule/runPolicy/labels?organization_id=%s" % self.workspaceId
        logger.debug("Requesting Labels %s" % mablUrl)
        response = self.httpRequest.get(mablUrl, headers=headers, contentType='application/json')
        data = json.loads(response.getResponse())
        logger.debug("Get Labels Response\n=============\n%s\n==================" % json.dumps(data, indent=4, sort_keys=True))

        if response.getStatus() not in HTTP_SUCCESS:
            logger.error("Get Labels Request Error (%s)" % response.getStatus())
            self.throw_error(response)

        data = json.loads(response.getResponse())
        labelNames = []
        for lab in data['labels']:
            labelNames.append(lab["name"])
        return labelNames


    def throw_error(self, response):
        logger.error("Error from MablService, HTTP Return: %s\n" % ( response.getStatus() ) )
        message = ""
        if response.getResponse():
            logger.error("Error from MablService, HTTP Return message: %s\n" % ( response.getResponse() ) )
            message = response.getResponse()
        raise Exception("Response status: %s, response message: %s " % (str(response.getStatus()), message))