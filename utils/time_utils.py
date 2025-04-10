from datetime import datetime, timezone


class TimeUtils:
    @staticmethod
    def get_current_timestamp() -> float:
        """Returns the current UTC timestamp as a float.

        Returns:
            float: Current UTC timestamp in seconds since the Unix epoch.
                  Includes microsecond precision after the decimal point.
        """

        # Example output: 1733456499.084317
        return datetime.now(timezone.utc).timestamp()
