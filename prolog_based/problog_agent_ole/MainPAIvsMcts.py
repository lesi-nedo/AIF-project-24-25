import asyncio
import typer


from typing_extensions import Annotated, Optional
from pyftg.socket.aio.gateway import Gateway
from pyftg.utils.logging import DEBUG, set_logging

from ProblogAgent import ProblogAgent

app = typer.Typer(pretty_exceptions_enable=False)


async def start_process(host:str , port: int, character: str = "ZEN", game_number: int = 1, plot_scenes: bool = False):
    gateway = Gateway(host, port)
    a2 = ProblogAgent(plot_scenes=plot_scenes)
    gateway.register_ai("ProblogAgent", a2)
    typer.echo(f"Running game Human vs {a2.name()}")
    await gateway.run_game([character, character], ["MctsAi23i","ProblogAgent"], game_number)


@app.command()
def main(
        host: Annotated[Optional[str], typer.Option(help="Host used by DareFightingICE")] = "127.0.0.1",
        port: Annotated[Optional[int], typer.Option(help="Port used by DareFightingICE")] = 31415,
        plot_scenes: Annotated[Optional[bool], typer.Option(help="Plot the scenes")] = False,
        # a1: Annotated[Optional[str], typer.Option(help="The AI name to use for player 1")] = None,
        # a2: Annotated[Optional[str], typer.Option(help="The AI name to use for player 2")] = None
    ):
    
    typer.echo(f"Starting the process with host: {host}, port: {port}")
    asyncio.run(start_process(host, port, plot_scenes=plot_scenes))
    

if __name__ == '__main__':
    set_logging(log_level=DEBUG)
    app()