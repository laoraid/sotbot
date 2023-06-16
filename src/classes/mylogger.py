import logging

logging.basicConfig(format="[%(asctime)s/%(levelname)s] %(message)s", datefmt="%Y-%m-%d %I:%M:%S")
botlogger = logging.getLogger("sotbot")
botlogger.setLevel(logging.INFO)
