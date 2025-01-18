import asyncio
import typer
import sys
import os
import pathlib
import numpy as np

sys.path.append(os.path.join(pathlib.Path(os.path.dirname(__file__)).parent, "prolog_agent_simo"))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(pathlib.Path(os.path.dirname(__file__)).parent.parent, "monte_carlo_tree_search"))


from typing_extensions import Annotated, Optional
from pyftg.socket.aio.gateway import Gateway
from pyftg.utils.logging import DEBUG, set_logging

from ProblogAgent import ProblogAgent

app = typer.Typer(pretty_exceptions_enable=False)
from prolog_based.prolog_agent_simo.PrologAI import PrologAI
from monte_carlo_tree_search.MctsAi import MctsAi
from StatsTracker import StatsTracker

async def start_process(
        host:str , port: int, character: str = "ZEN", game_number: int = 1, keep_stats: bool = False, 
        plot_scenes: bool = False, simo_agent: bool = False, marco_agent: bool = False, fightice_agent: bool = False
    ):


    gateway = Gateway(host, port)
        
    if simo_agent:
        a1 = PrologAI()
        gateway.register_ai("PrologAI", a1)
        name_agent = "PrologAI"
    if marco_agent:
        a1 = MctsAi(exploration_constant=np.sqrt(2), iteration_limit=3)
        gateway.register_ai("MctsAi", a1)
        name_agent = "MctsAi"
    if fightice_agent:
        name_agent = "MctsAi23i"

    if keep_stats:
        stats_tracker= StatsTracker(name_agent, "ProblogAgent")
        a2 = ProblogAgent(plot_scenes=plot_scenes, stats_tracker=stats_tracker)
    else:
        a2 = ProblogAgent(plot_scenes=plot_scenes)
    gateway.register_ai("ProblogAgent", a2)
    await gateway.run_game([character, character], [name_agent,"ProblogAgent"], game_number)
    
    # a1 = MinimaxAI()
    # gateway.register_ai("MinimaxAI", a1)
    # name_minimax = "MinimaxAI"
    # await gateway.run_game([character, character], [name_minimax,"ProblogAgent"], game_number)

    # name = "MctsAi23i"
    # await gateway.run_game([character, character], [name,"ProblogAgent"], game_number)

    
    



@app.command()
def main(
        host: Annotated[Optional[str], typer.Option(help="Host used by DareFightingICE")] = "127.0.0.1",
        port: Annotated[Optional[int], typer.Option(help="Port used by DareFightingICE")] = 31415,
        plot_scenes: Annotated[Optional[bool], typer.Option(help="Plot the scenes")] = False,
        # a1: Annotated[Optional[str], typer.Option(help="The AI name to use for player 1")] = None,
        # a2: Annotated[Optional[str], typer.Option(help="The AI name to use for player 2")] = None
    ):
    
    typer.echo(f"Starting the process with host: {host}, port: {port}")
    asyncio.run(start_process(host, port, plot_scenes=plot_scenes, fightice_agent=True))
    

if __name__ == '__main__':
    set_logging(log_level=DEBUG)
    app()