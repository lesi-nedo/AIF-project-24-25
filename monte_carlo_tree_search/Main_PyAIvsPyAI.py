import asyncio
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import typer
from typing_extensions import Annotated, Optional

from KickAI import KickAI
from MctsAi import MctsAi
from pyftg.socket.aio.gateway import Gateway
from pyftg.utils.logging import DEBUG, set_logging
from prolog_based.problog_agent_ole.ProblogAgent import ProblogAgent
from prolog_based.prolog_agent_simo.PrologAI import PrologAI
app = typer.Typer(pretty_exceptions_enable=False)


async def start_process(
    host: str,
    port: int,
    keyboard: bool = False,
    character: str = "ZEN",
    game_num: int = 1,
    plot_scenes: bool=False
):
    plot_scenes = plot_scenes
    gateway = Gateway(host, port)
    agent1 = KickAI()
    agent1 = ProblogAgent(plot_scenes)
    agent1 = PrologAI()
    agent2 = MctsAi(plot_scenes)
    gateway.register_ai("MctsAi", agent2)
    if not keyboard:
        gateway.register_ai("KickAI", agent1)
        # gateway.register_ai("ProblogAgent", agent1)
        gateway.register_ai("PrologAI", agent1)
        await gateway.run_game(
            [character, character], ["PrologAI", "MctsAi"], game_num
        )
    else:
        await gateway.run_game(
            [character, character], ["Keyboard", "MctsAi"], game_num
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
