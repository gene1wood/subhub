#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

import newrelic.agent
import serverless_wsgi

serverless_wsgi.TEXT_MIME_TYPES.append("application/custom+json")

from os.path import join, dirname, realpath
# First some funky path manipulation so that we can work properly in
# the AWS environment
sys.path.insert(0, join(dirname(realpath(__file__)), 'src'))

newrelic.agent.initialize()

from aws_xray_sdk.core import xray_recorder, patch_all
from aws_xray_sdk.core.context import Context
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

from sub.app import create_app
from shared.log import get_logger

logger = get_logger()

xray_recorder.configure(service="fxa.sub")
patch_all()

sub_app = create_app()
XRayMiddleware(sub_app.app, xray_recorder)

# NOTE: The context object has the following available to it.
#   https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html#python-context-object-props
# NOTE: Available environment passed to the Flask from serverless-wsgi
#   https://github.com/logandk/serverless-wsgi/blob/2911d69a87ae8057110a1dcf0c21288477e07ce1/serverless_wsgi.py#L126
@newrelic.agent.lambda_handler()
def handle(event, context):
    try:
        logger.info("handling sub event", subhub_event=event, context=context)
        return serverless_wsgi.handle_request(sub_app.app, event, context)
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("exception occurred", subhub_event=event, context=context, error=e)
        # TODO: Add Sentry exception catch here
        raise