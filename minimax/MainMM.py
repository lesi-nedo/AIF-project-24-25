import asyncio

import typer
from pyftg.socket.aio.gateway import Gateway
from pyftg.utils.logging import set_logging, DEBUG
from typing_extensions import Annotated, Optional

from minimax.MinimaxAI import MinimaxAI

app = typer.Typer(pretty_exceptions_enable=False)

character = "ZEN"

async def start_process(
        host: str,
        port: int,
        character: str = character,
        game_num: int = 1,
):
    gateway = Gateway(host, port)
    agent2 = MinimaxAI(depth=1, character=character)
    gateway.register_ai("MinimaxAI", agent2)
    await gateway.run_game(
        [character, character], ["Keyboard", "MinimaxAI"], game_num
    )


@app.command()
def main(
        host: Annotated[
            Optional[str], typer.Option(help="Host used by DareFightingICE")
        ] = "127.0.0.1",
        port: Annotated[
            Optional[int], typer.Option(help="Port used by DareFightingICE")
        ] = 31415,
):
    asyncio.run(start_process(host, port))


if __name__ == "__main__":
    set_logging(log_level=DEBUG)
    app()
