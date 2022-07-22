#
# Copyright 2022 DIGITAL.AI
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import mabl.MablClient
from mabl.MablClient import Mabl_Client
import logging

logger = logging.getLogger('mabl.'+'waitForTest')

#logger = LoggerFactory.getLogger("Mabl")
mablObj = Mabl_Client.create_client(mablServer, token, None, failTaskOnFailedTest)
logger.debug("failTaskOnFailedTest = %s", failTaskOnFailedTest)
method = "mabl_waitfortest"

logger.debug("##### Start Wait For Script ####")
logger.debug("Waiting for test ID %s" % testId)
isDone = False
count = 1
hadFailure = False
if not isDone:
    call = getattr(mablObj, method)
    results = call(locals())
    executions = results['executions']
    numberOfExecutions = len(executions)
    if numberOfExecutions == 0:
        logger.error("ERROR: No tests ran")
        print("# ERROR No tests ran")
        exit(-1)
    isDone = True
    idx = 1
    for execution in executions:
        status = execution['plan_execution']['status']
        logger.debug("%s %s of %s Status = %s" % (count, idx, numberOfExecutions, status))
        idx += 1
        if status == "scheduled":
            isDone = False
    count += 1
    if not isDone:
        logger.debug("Reschedule `waitForTest` in %s seconds" % locals()['pollTime'])
        task.schedule("mabl/waitForTest.py", locals()['pollTime'])

if isDone:
    for key,value in results['output'].items():
        logger.debug("%s = %s, %s  %s" % (key, value, 'failed' in key,  value > 0))
        locals()[key] = value
        if 'failed' in key.lower() and value > 0:
            hadFailure = True



    print("# Journey URLs:")
    for url in results['output']['journeyUrl']:
        print("* %s" % url)

    if hadFailure and mablObj.failTaskOnFailedTest:
        logger.debug("At lease one test has failed and 'Fail Task On Failed Test' flag is set to true")
        raise Exception("At lease one test has failed and 'Fail Task On Failed Test' flag is set to true")
