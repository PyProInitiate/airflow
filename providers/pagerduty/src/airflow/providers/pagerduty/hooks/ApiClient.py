from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pagerduty

from airflow.exceptions import AirflowException
from airflow.hooks.base import BaseHook

if TYPE_CHECKING:
    from datetime import datetime

class ApiClient:
    """
    The ApiClient is a client for the PagerDuty API.
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
    def after_set_api_key(self) -> None:
        """
        After setting the API key, this method is called to initialize the session.
        """
        self._session = pagerduty.APISession(self.integration_key)
        self._session.headers.update(self.prepare_headers())
    
    @property
    def api_key(self) -> str:
        """
        The API key used for authentication.
        """
        return self._session.api_key

    @property
    def auth_header(self) -> dict:
        """
        The authentication header used for API requests.
        """
        return self._session.auth_header

    log=None
    max_http_attempts = 10
    max_network_attempts = 3

    def normalize_params(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize the parameters for API requests.
        """
        return params
    
    def normalize_url(self, url: str) -> str:
        """
        Normalize the URL for API requests.
        """
        return url

    parent = None

    permitted_methods = [
        'GET',
        'POST',
        'PUT',
        'DELETE',
        'PATCH',
    ]

    def postprocess(response: Any) -> Any:
        """
        Post-process the response from the API.
        """
        return response

    def prepare_headers(method,user_headers={})->dict:

        return user_headers



    print_debug = False
    if print_debug is True:
        log = logging.DEBUG
        """
        Print debug information.
        """
        print(log)
    log = logging.NOTSET

    def request(method, url, **kwargs) -> Any:
        """
        Make a request to the PagerDuty API.

        :param method: The HTTP method to use (GET, POST, PUT, DELETE).
        :param url: The URL for the API endpoint.
        :param kwargs: Additional arguments to pass to the request.
        :return: The response from the API.
        """
        # Perform the request using the session
        response = self._session.request(method, url, params=params, data=data, headers=headers, **kwargs)
        return response

    retry = {}

    sleep_timer = 1.5

    sleep_timer_base = 2

    stagger_cooldown: float

    timeout = 60

    trunc_key:str