import configparser
from dataclasses import dataclass


@dataclass
class Bot:
    TOKEN: str
    way: str


@dataclass
class Config:
    bot: Bot


def load_config(path: str):
    config = configparser.ConfigParser()
    config.read(path)

    bot = config["bot"]

    return Config(
        bot=Bot(
            TOKEN=bot["TOKEN"],
            way=bot['way']
        )
    )
