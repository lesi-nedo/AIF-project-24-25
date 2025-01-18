import asyncio
import typer
from typing_extensions import Annotated, Optional
from pyftg.utils.logging import DEBUG, set_logging
from MainGameAgetVsMyAgent import start_process

app = typer.Typer(pretty_exceptions_enable=False)



@app.command()
def main(
        host: Annotated[Optional[str], typer.Option(help="Host used by DareFightingICE")] = "127.0.0.1",
        port: Annotated[Optional[int], typer.Option(help="Port used by DareFightingICE")] = 31415,
        plot_scenes: Annotated[Optional[bool], typer.Option(help="Plot the scenes")] = False,
        # a1: Annotated[Optional[str], typer.Option(help="The AI name to use for player 1")] = None,
        # a2: Annotated[Optional[str], typer.Option(help="The AI name to use for player 2")] = None
    ):
    
    typer.echo(f"Starting the process with host: {host}, port: {port}")
    asyncio.run(start_process(host, port, plot_scenes=plot_scenes, marco_agent=True, keep_stats=True))
    

if __name__ == '__main__':
    set_logging(log_level=DEBUG)
    app()