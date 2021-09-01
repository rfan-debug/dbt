import os
import multiprocessing
if os.name != 'nt':
    # https://bugs.python.org/issue41567
    import multiprocessing.popen_spawn_posix  # type: ignore
from pathlib import Path
from typing import Optional


STRICT_MODE = False  # Only here for backwards compatibility
FULL_REFRESH = False  # subcommand
STORE_FAILURES = False  # subcommand

# Global CLI commands
USE_EXPERIMENTAL_PARSER = None
WARN_ERROR = None
WRITE_JSON = None
PARTIAL_PARSE = None
USE_COLORS = None
PROFILES_DIR = None
DEBUG = None
LOG_FORMAT = None
NO_VERSION_CHECK = None
FAIL_FAST = None
SEND_ANONYMOUS_USAGE_STATS = None
PRINTER_WIDTH = None

# Global CLI defaults. These flags are set from three places:
# CLI args, environment variables, and user_config (profiles.yml).
# Environment variables use the pattern 'DBT_{flag name}', like DBT_PROFILES_DIR
flag_defaults = {
    "USE_EXPERIMENTAL_PARSER": False,
    "WARN_ERROR": False,
    "WRITE_JSON": True,
    "PARTIAL_PARSE": False,
    "USE_COLORS": True,
    "PROFILES_DIR": None,
    "DEBUG": False,
    "LOG_FORMAT": None,
    "NO_VERSION_CHECK": False,
    "FAIL_FAST": False,
    "SEND_ANONYMOUS_USAGE_STATS": True,
    "PRINTER_WIDTH": 80
}


def env_set_truthy(key: str) -> Optional[str]:
    """Return the value if it was set to a "truthy" string value, or None
    otherwise.
    """
    value = os.getenv(key)
    if not value or value.lower() in ('0', 'false', 'f'):
        return None
    return value


def env_set_path(key: str) -> Optional[Path]:
    value = os.getenv(key)
    if value is None:
        return value
    else:
        return Path(value)


SINGLE_THREADED_WEBSERVER = env_set_truthy('DBT_SINGLE_THREADED_WEBSERVER')
SINGLE_THREADED_HANDLER = env_set_truthy('DBT_SINGLE_THREADED_HANDLER')
MACRO_DEBUGGING = env_set_truthy('DBT_MACRO_DEBUGGING')
DEFER_MODE = env_set_truthy('DBT_DEFER_TO_STATE')
ARTIFACT_STATE_PATH = env_set_path('DBT_ARTIFACT_STATE_PATH')


def _get_context():
    # TODO: change this back to use fork() on linux when we have made that safe
    return multiprocessing.get_context('spawn')


# This is not a flag, it's a place to store the lock
MP_CONTEXT = _get_context()


def set_from_args(args, user_config):
    global STRICT_MODE, FULL_REFRESH, WARN_ERROR, \
        USE_EXPERIMENTAL_PARSER, WRITE_JSON, PARTIAL_PARSE, USE_COLORS, \
        STORE_FAILURES, PROFILES_DIR, DEBUG, LOG_FORMAT,\
        NO_VERSION_CHECK, FAIL_FAST, SEND_ANONYMOUS_USAGE_STATS, PRINTER_WIDTH

    STRICT_MODE = False  # backwards compatibility
    # cli args without user_config or env var option
    FULL_REFRESH = getattr(args, 'full_refresh', FULL_REFRESH)
    STORE_FAILURES = getattr(args, 'store_failures', STORE_FAILURES)

    # global cli flags with env var and user_config alternatives
    USE_EXPERIMENTAL_PARSER = get_flag_value('USE_EXPERIMENTAL_PARSER', args, user_config)
    WARN_ERROR = get_flag_value('WARN_ERROR', args, user_config)
    WRITE_JSON = get_flag_value('WRITE_JSON', args, user_config)
    PARTIAL_PARSE = get_flag_value('PARTIAL_PARSE', args, user_config)
    USE_COLORS = get_flag_value('USE_COLORS', args, user_config)
    PROFILES_DIR = get_flag_value('PROFILES_DIR', args, user_config)
    DEBUG = get_flag_value('DEBUG', args, user_config)
    LOG_FORMAT = get_flag_value('LOG_FORMAT', args, user_config)
    NO_VERSION_CHECK = get_flag_value('NO_VERSION_CHECK', args, user_config)
    FAIL_FAST = get_flag_value('FAIL_FAST', args, user_config)
    SEND_ANONYMOUS_USAGE_STATS = get_flag_value('SEND_ANONYMOUS_USAGE_STATS', args, user_config)
    PRINTER_WIDTH = get_flag_value('PRINTER_WIDTH', args, user_config)


def get_flag_value(flag, args, user_config):
    lc_flag = flag.lower()
    flag_value = getattr(args, lc_flag, None)
    if flag_value is None:
        # Environment variables use pattern 'DBT_{flag name}'
        env_flag = f"DBT_{flag}"
        env_value = os.getenv(env_flag)
        if env_value is not None:
            if flag in ['LOG_FORMAT', 'PROFILES_DIR', 'PRINTER_WIDTH']:
                flag_value = env_value
            else:
                flag_value = True if env_value else False
        elif user_config is not None and getattr(user_config, lc_flag, None):
            flag_value = getattr(user_config, lc_flag)
        else:
            flag_value = flag_defaults[flag]
    if flag == 'PROFILES_DIR' and flag_value:
        flag_value = os.path.abspath(flag_value)

    return flag_value
