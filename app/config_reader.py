import configparser
from dataclasses import dataclass


@dataclass
class Bot:
    TOKEN: str
    admin_id: int
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
            admin_id=int(bot["admin_id"]),
            way=bot['way']
        )
    )
