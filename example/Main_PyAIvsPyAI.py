import asyncio

import typer
from typing_extensions import Annotated, Optional

from KickAI import KickAI
from DisplayInfo import DisplayInfo
from pyftg.socket.aio.gateway import Gateway
from pyftg.utils.logging import DEBUG, set_logging

app = typer.Typer(pretty_exceptions_enable=False)


async def start_process(
    host: str,
    port: int,
    keyboard: bool = False,
    character: str = "ZEN",
    game_num: int = 1,
):

    gateway = Gateway(host, port)
    agent1 = KickAI()
    agent2 = DisplayInfo()
    gateway.register_ai("DisplayInfo", agent2)
    if not keyboard:
        gateway.register_ai("KickAI", agent1)
        await gateway.run_game(
            [character, character], ["KickAI", "DisplayInfo"], game_num
        )
    else:
        await gateway.run_game(
            [character, character], ["Keyboard", "DisplayInfo"], game_num
        )


@app.command()
def main(
    host: Annotated[
        Optional[str], typer.Option(help="Host used by DareFightingICE")
    ] = "127.0.0.1",
    port: Annotated[
        Optional[int], typer.Option(help="Port used by DareFightingICE")
    ] = 31415,
    keyboard: Annotated[bool, typer.Option(help="Key to start the game")] = False,
):
    asyncio.run(start_process(host, port, keyboard))


if __name__ == "__main__":
    set_logging(log_level=DEBUG)
    app()
