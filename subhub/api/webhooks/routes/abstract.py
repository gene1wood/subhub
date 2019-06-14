from abc import ABC

import flask

from subhub.log import get_logger

logger = get_logger()


class AbstractRoute(ABC):
    def __init__(self, payload):
        self.payload = payload

    def report_route(self, payload: dict, sent_system: str):
        logger.info("report route", payload=payload, sent_system=sent_system)
        existing = flask.g.webhook_table.get_event(payload["event_id"])
        if not existing:
            created = flask.g.webhook_table.new_event(
                event_id=payload["event_id"], sent_system=sent_system
            )
            saved = flask.g.webhook_table.save_event(created)
            logger.info("new event", created=created, saved=saved)
        else:
            updated = flask.g.webhook_table.append_event(
                event_id=payload["event_id"], sent_system=sent_system
            )
            logger.info("updated event", existing=existing, updated=updated)

    def report_route_error(self, payload):
        logger.error("report route error", payload=payload)
