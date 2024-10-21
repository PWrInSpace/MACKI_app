import os
from src.cameras.frame_handlers import FrameDisplayFormats


CONFIG_DIR = os.path.join(os.getcwd(), "config")

COMMANDS_CONFIG_FILE = os.path.join(CONFIG_DIR, "service_commands.json")
DATA_PLOT_CONFIG_FILE = os.path.join(CONFIG_DIR, "experiment_data_plot.json")
DATA_TEXT_CONFIG_FILE = os.path.join(CONFIG_DIR, "experiment_data_text.json")
PARSER_CONFIG_FILE = os.path.join(CONFIG_DIR, "data_parser.json")

RESOURCES_DIR = os.path.join(os.getcwd(), "resources")
OCTOPUS_EXP_WIN = os.path.join(RESOURCES_DIR, "octopus.svg")
OCTOPUS_CAM_WIN = os.path.join(RESOURCES_DIR, "octopus_apple.png")
OCTOPUS_SERIAL_WIN = os.path.join(RESOURCES_DIR, "octopus.png")


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
VIDEO_RESOLUTION = (1936, 1216)
VIDEO_DIR = "data"
