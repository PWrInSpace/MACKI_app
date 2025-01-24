import os
from src.cameras.frame_handlers import FrameDisplayFormats


CONFIG_DIR = os.path.join(os.getcwd(), "config")

COMMANDS_CONFIG_FILE = os.path.join(CONFIG_DIR, "service_commands.json")
DATA_PLOT_CONFIG_FILE = os.path.join(CONFIG_DIR, "experiment_data_plot.json")
DATA_TEXT_CONFIG_FILE = os.path.join(CONFIG_DIR, "experiment_data_text.json")
PARSER_CONFIG_FILE = os.path.join(CONFIG_DIR, "data_parser.json")
PROCEDURES_CONFIG_FILE = os.path.join(CONFIG_DIR, "procedures.json")

RESOURCES_DIR = os.path.join(os.getcwd(), "resources")
OCTOPUS_EXP_WIN = os.path.join(RESOURCES_DIR, "octopus.svg")
OCTOPUS_CAM_WIN = os.path.join(RESOURCES_DIR, "octopus_apple.png")
OCTOPUS_SERIAL_WIN = os.path.join(RESOURCES_DIR, "octopus.png")
OCTOPUS_PROC_CONFIG_WIN = os.path.join(RESOURCES_DIR, "octopus_procedure_config.png")


# TEMPORARY
MAKO_CONFIG_FILE = os.path.join("config", "mako.xml")
ALVIUM_CONFIG_FILE = os.path.join("config", "alvium2.xml")
CAMERA_CONFIG = os.path.join("config", "DEV_000A4727B2BF_settings.xml")
# MAKO_CONFIG_FILE = None
# ALVIUM_CONFIG_FILE = None

MACKI_LOGO_PATH = os.path.join("resources", "MACKI_patch.png")
DEFAULT_FRAME_SIZE = (500, 500)
MINI_FRAME_SIZE = (300, 300)
FRAME_FORMAT = FrameDisplayFormats.RGB

VIDEO_FPS = 10
VIDEO_RESOLUTION = (1216, 1936)
VIDEO_DIR = "data"


LOG_DIR = os.path.join(os.getcwd(), "data", "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": LOG_FILE,
            "formatter": "standard",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
