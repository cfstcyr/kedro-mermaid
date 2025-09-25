import logging
import os


def parse_list(ctx, param, value: str) -> list[str] | None:
    return [x.strip() for x in value.split(",")] if value else None

def silence_kedro_logs():
    """Disable Kedro logging so stdout is fully under our control."""
    # Prevent Kedro from loading conf/logging.yml
    os.environ["KEDRO_LOGGING_CONFIG"] = "null"
    # Remove any handlers already attached
    root = logging.getLogger()
    for h in root.handlers[:]:
        root.removeHandler(h)
    # Disable all logging
    logging.disable(logging.CRITICAL)