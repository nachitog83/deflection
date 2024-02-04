import logging
from datetime import datetime, timedelta

from django.conf import settings

from chat.exceptions import ThrottlingConfigurationError, ThrottlingError

logger = logging.getLogger("chat")


class MessageThrottler:
    UNITS = ["year", "month", "day", "hour", "minute", "second"]

    def __init__(self):
        amount: str = settings.WEBSOCKET_THROTTLE.split("/")[0]
        unit: str = settings.WEBSOCKET_THROTTLE.split("/")[1]

        if not amount.isdigit() or unit not in self.UNITS:
            raise ThrottlingConfigurationError(f"Wrong format for throttling config: {settings.WEBSOCKET_THROTTLE}")

        self.amount = int(amount)
        self.unit = unit

        self.set_current_time()
        self.set_new_limit()

    def set_current_time(self):
        self.now = datetime.now()

    def set_new_limit(self):
        self.limit = self.now + timedelta(**{self.unit + "s": 1})
        self.count = 0

    def check_throttle(self):
        self.set_current_time()
        if self.now < self.limit and self.count >= self.amount:
            raise ThrottlingError()
        elif self.now >= self.limit:
            self.set_new_limit()
        self.count += 1
