import logging
from datetime import datetime, timedelta

from django.conf import settings

from chat.exceptions import ThrottlingConfigurationError, ThrottlingError

logger = logging.getLogger("chat")


class MessageThrottler:
    """
    Websocket message throttle control.
    Based con settings config, it will throttle message if limit is passed

    Raises:
        ThrottlingConfigurationError: Config format is incorrect. Should be as
        example: "1/second", "100/minute", "100000/month". You can deactivate throttling
        by setting config as "UNLIMITED"
        ThrottlingError: User has passed message limit
    """

    UNITS = ["year", "month", "day", "hour", "minute", "second"]
    DEFAULT = "10/second"
    unlimited_messages = False

    def __init__(self):
        if settings.WEBSOCKET_THROTTLE.lower() == "unlimited":
            self.unlimited_messages = True
        else:
            self._init_vars()

    def _init_vars(self):
        try:
            amount, unit = settings.WEBSOCKET_THROTTLE.split("/")
        except ValueError:
            amount, unit = self.get_defaults()

        if not amount.isdigit() or unit not in self.UNITS:
            amount, unit = self.get_defaults()

        self.amount = int(amount)
        self.unit = unit

        self._set_current_time()
        self._set_new_limit()

    def get_defaults(self):
        logger.warning(
            f"Wrong format for throttling config: {settings.WEBSOCKET_THROTTLE}. Setting default {self.DEFAULT}"
        )
        return self.DEFAULT.split("/")

    def _set_current_time(self):
        self._now = datetime.now()

    def _set_new_limit(self):
        self._limit = self._now + timedelta(**{self.unit + "s": 1})
        self._count = 0

    def check_throttle(self):
        if self.unlimited_messages:
            return
        self._set_current_time()
        if self._now < self._limit and self._count >= self.amount:
            raise ThrottlingError()
        elif self._now >= self._limit:
            self._set_new_limit()
        self._count += 1
