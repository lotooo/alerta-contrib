
import json
import logging
import os
import requests
import traceback
import xml.etree.ElementTree as ET

LOG = logging.getLogger('alerta.plugins.rundeck')
LOG.setLevel(logging.DEBUG)

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0

from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.rundeck')

if app.config.get('RUNDECK_BASE_URL', False):
    RUNDECK_BASE_URL=app.config.get('RUNDECK_BASE_URL')
else:
    RUNDECK_BASE_URL=os.environ.get('RUNDECK_BASE_URL', False)

if app.config.get('RUNDECK_TOKEN', False):
    RUNDECK_TOKEN=app.config.get('RUNDECK_TOKEN')
else:
    RUNDECK_TOKEN=os.environ.get('RUNDECK_TOKEN', False)

try:
    RUNDECK_JOB_MAP = app.config.get('RUNDECK_JOB_MAP')
except:
    LOG.error("Unable to load RUNDECK_JOB_MAP json")
    RUNDECK_JOB_MAP = dict()

RUNDECK_HEADERS = {
    'Content-Type': 'application/json',
    'X-Rundeck-Auth-Token': RUNDECK_TOKEN,
}


class ServiceIntegration(PluginBase):

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert, **kwargs):
        if alert.attributes.get('rundeck_execution'):
            LOG.info("A rundeck job has already been triggered for this alert")
            return

        # Extract the job to execute based on the event name 
        job_id =  RUNDECK_JOB_MAP.get(alert.event)
        if not job_id:
            LOG.debug("No rundeck job id found for %s" % alert.event)
            return
        
        payload = {
            "options": {
                "environment": alert.environment,
                "event": alert.event,
                "id": alert.id,
                "resource": alert.resource,
                "services": ','.join(alert.service),
                "severity": alert.severity,
                "status": alert.status
            }
        }

        LOG.info("Executing job %s" % job_id)  
        LOG.debug(payload)
        r = requests.post("%s/20/job/%s/run" % (RUNDECK_BASE_URL, job_id), headers=RUNDECK_HEADERS, json=payload)
        LOG.debug("Response from rundeck:")
        LOG.debug(r.content)
        try:
            execution_url = ET.fromstring(r.content).find("./execution").attrib.get("permalink")
            LOG.info("Follow execution: %s" % execution_url)
            alert.attributes['rundeck_execution'] = "<a href='%s'>%s</a>" % (execution_url,execution_url)
        except:
            LOG .erro("Impossible to extract execution id")
        return alert

    def status_change(self, alert, status, text, **kwargs):
        return
