#
# Copyright 2021 DIGITAL.AI
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import mabl.MablClient
from mabl.MablClient import Mabl_Client
import org.slf4j.LoggerFactory as LoggerFactory

logger = LoggerFactory.getLogger("Mabl")
mablObj = Mabl_Client.create_client(mablServer, token)
method = "mabl_waitfortest"

logger.error("##### Start Wait For Script ####")
logger.error("Waiting for test ID %s" % testId)
isDone = False
count = 1
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
        logger.error("Reschedule `waitForTest` in %s seconds" % locals()['pollTime'])
        task.schedule("mabl/waitForTest.py", locals()['pollTime'])

if isDone:
    for key,value in results['output'].items():
        logger.error("%s = %s" % (key, value))
        locals()[key] = value

    print("# Journey URLs:")
    for url in results['output']['journeyUrl']:
        print("* %s" % url)
