from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pagerduty

from airflow.exceptions import AirflowException
from airflow.hooks.base import BaseHook

if TYPE_CHECKING:
    from datetime import datetime

class EventsAPiV2Client:
    """
    The EventsAPiV2Client is a client for the PagerDuty Events API V2.
    It can be used to send events to PagerDuty, such as triggering incidents or acknowledging them.
    """

    def __init__(self, integration_key: str | None = None, pagerduty_events_conn_id: str | None = None) -> None:
        super().__init__()
        self.integration_key = None
        self._session = None

        if pagerduty_events_conn_id is not None:
            conn = self.get_connection(pagerduty_events_conn_id)
            self.integration_key = conn.get_password()

        if integration_key is not None:  # token takes higher priority
            self.integration_key = integration_key

        if self.integration_key is None:
            raise AirflowException(
                "Cannot get token: No valid integration key nor pagerduty_events_conn_id supplied."
            )
    def acknowledge_event(self, event_id: str) -> None:
        """
        Acknowledge an event in PagerDuty.

        :param event_id: The ID of the event to acknowledge.
        """
        try:
            self._session.acknowledge_event(event_id)
        except pagerduty.PagerDutyError as e:
            raise AirflowException(f"Failed to acknowledge event: {e}") from e

    def post_event(self, payload: dict[str, Any]) -> str:
        """
        Post an event to PagerDuty.

        :param payload: The event payload to send to PagerDuty.
        :return: The ID of the created event.
        """
        try:
            response = self._session.post_event(payload)
            return response['event']['id']
        except pagerduty.PagerDutyError as e:
            raise AirflowException(f"Failed to post event: {e}") from e

    def prepare_headers(self) -> dict[str, str]:
        """
        Prepare the headers for the API request.

        :return: The headers for the API request.
        """
        return {
            'Authorization': f'Token token={self.integration_key}',
            'Content-Type': 'application/json',
        }
    def resolve_event(self, event_id: str) -> None:
        """
        Resolve an event in PagerDuty.

        :param event_id: The ID of the event to resolve.
        """
        try:
            self._session.resolve_event(event_id)
        except pagerduty.PagerDutyError as e:
            raise AirflowException(f"Failed to resolve event: {e}") from e

    def send_change_event(
        self,
        payload: dict[str, Any],
        event_type: str = "trigger",
        routing_key: str | None = None,
    ) -> str:
        """
        Send a change event to PagerDuty.

        :param payload: The event payload to send to PagerDuty.
        :param event_type: The type of event to send (trigger, acknowledge, resolve).
        :param routing_key: The routing key for the event.
        :return: The ID of the created event.
        """
        if routing_key is None:
            routing_key = self.integration_key

        try:
            response = self._session.send_event(payload, event_type, routing_key)
            return response['event']['id']
        except pagerduty.PagerDutyError as e:
            raise AirflowException(f"Failed to send change event: {e}") from e
    
    def send_event(
        self,
        summary: str,
        severity: str,
        source: str,
        custom_details: dict[str, Any] | None = None,
        component: str | None = None,
        group: str | None = None,
        class_type: str | None = None,
        action: str = "trigger",
        dedup_key: str | None = None,
        images: list[dict[str, Any]] | None = None,
        links: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Send an event to PagerDuty.

        :param summary: The summary of the event.
        :param severity: The severity of the event.
        :param source: The source of the event.
        :param custom_details: Custom details for the event.
        :param component: The component of the event.
        :param group: The group of the event.
        :param class_type: The class type of the event.
        :param action: The action to take (trigger, acknowledge, resolve).
        :param dedup_key: A deduplication key for the event.
        :param images: Images associated with the event.
        :param links: Links associated with the event.
        :return: The response from PagerDuty.
        """
        payload = self.prepare_payload(
            summary=summary,
            severity=severity,
            source=source,
            custom_details=custom_details,
            component=component,
            group=group,
            class_type=class_type,
            action=action,
            dedup_key=dedup_key,
            images=images,
            links=links,
        )
        return self.post_event(payload)
    
    def submit_event(
        self,
        summary: str,
        severity: str,
        source: str,
        custom_details: dict[str, Any] | None = None,
        component: str | None = None,
        group: str | None = None,
        class_type: str | None = None,
        action: str = "trigger",
        dedup_key: str | None = None,
        images: list[dict[str, Any]] | None = None,
        links: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Submit an event to PagerDuty.

        :param summary: The summary of the event.
        :param severity: The severity of the event.
        :param source: The source of the event.
        :param custom_details: Custom details for the event.
        :param component: The component of the event.
        :param group: The group of the event.
        :param class_type: The class type of the event.
        :param action: The action to take (trigger, acknowledge, resolve).
        :param dedup_key: A deduplication key for the event.
        :param images: Images associated with the event.
        :param links: Links associated with the event.
        :return: The response from PagerDuty.
        """
        return self.send_event(
            summary=summary,
            severity=severity,
            source=source,
            custom_details=custom_details,
            component=component,
            group=group,
            class_type=class_type,
            action=action,
            dedup_key=dedup_key,
            images=images,
            links=links,
        )
    
    def trigger_event(
        self,
        summary: str,
        severity: str,
        source: str,
        custom_details: dict[str, Any] | None = None,
        component: str | None = None,
        group: str | None = None,
        class_type: str | None = None,
        action: str = "trigger",
        dedup_key: str | None = None,
        images: list[dict[str, Any]] | None = None,
        links: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Trigger an event in PagerDuty.

        :param summary: The summary of the event.
        :param severity: The severity of the event.
        :param source: The source of the event.
        :param custom_details: Custom details for the event.
        :param component: The component of the event.
        :param group: The group of the event.
        :param class_type: The class type of the event.
        :param action: The action to take (trigger, acknowledge, resolve).
        :param dedup_key: A deduplication key for the event.
        :param images: Images associated with the event.
        :param links: Links associated with the event.
        :return: The response from PagerDuty.
        """
        return self.send_event(
            summary=summary,
            severity=severity,
            source=source,
            custom_details=custom_details,
            component=component,
            group=group,
            class_type=class_type,
            action=action,
            dedup_key=dedup_key,
            images=images,
            links=links,
        )