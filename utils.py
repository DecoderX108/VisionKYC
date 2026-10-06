import yaml
import os
import json
import logging
import time

LOGGING_STR = "[%(asctime)s: %(levelname)s: %(module)s]: %(message)s"


def setup_logging(log_dir="logs"):
    """Log to logs/ekyc_logs.log AND to stdout (so `docker logs` shows it).

    Safe to call from several modules: logging.basicConfig is a no-op after
    the first call.
    """
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format=LOGGING_STR,
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "ekyc_logs.log"), mode="a"),
            logging.StreamHandler(),
        ],
    )


def file_exists(file_path):
    is_exist = os.path.exists(file_path)
    if is_exist:
        logging.info(f"File is exis for {file_path}")
        return True

def read_yaml(path_to_yaml:str) -> dict:
    with open(path_to_yaml) as yaml_file:
        content = yaml.safe_load(yaml_file)
    logging.info(f"yaml  file: {path_to_yaml} loaded successfully")
    return content

def create_dirs(dirs: list):
    for dir in dirs:
        os.makedirs(dir, exist_ok=True)
        logging.info(f"Directory is created at {dir}")
