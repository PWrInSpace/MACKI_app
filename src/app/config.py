import os

CONFIG_DIR = os.path.join(os.getcwd(), "config")

COMMANDS_CONFIG_FILE = os.path.join(CONFIG_DIR, "service_commands.json")
DATA_PLOT_CONFIG_FILE = os.path.join(CONFIG_DIR, "experiment_data_plot.json")
DATA_TEXT_CONFIG_FILE = os.path.join(CONFIG_DIR, "experiment_data_text.json")
PARSER_CONFIG_FILE = os.path.join(CONFIG_DIR, "data_parser.json")

RESOURCES_DIR = os.path.join(os.getcwd(), "resources")
OCTOPUS_EXP_WIN = os.path.join(RESOURCES_DIR, "octopus.svg")
OCTOPUS_CAM_WIN = os.path.join(RESOURCES_DIR, "octopus_apple.png")
OCTOPUS_SERIAL_WIN = os.path.join(RESOURCES_DIR, "octopus.png")
