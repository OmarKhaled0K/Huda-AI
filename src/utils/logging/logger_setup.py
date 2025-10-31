import logging.config
import json
from pathlib import Path
import yaml
def setup_logger():
    # Get the current directory where logger_setup.py is located
    current_dir = Path(__file__).resolve().parent
    config_path = current_dir / "logging_config.yml"

    
    # Create logs directory if it doesn't exist
    logs_dir = current_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # # Load the config from the JSON file
    # with open(config_path, "r") as f:
    #     config = json.load(f)
    
    # Load the config from the YAML file
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Update the file handlers with absolute paths
    for handler in config.get("handlers", {}).values():
        if "filename" in handler:
            relative_path = handler["filename"]
            handler["filename"] = str(logs_dir / Path(relative_path).name)
    
    # Configure logging
    logging.config.dictConfig(config)
    return logging.getLogger("app")
