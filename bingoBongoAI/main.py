import asyncio
import typer
from typing_extensions import Annotated, Optional

# Import degli agenti definiti
from KickAI import KickAI
from DisplayInfo import DisplayInfo
from pyftg.socket.aio.gateway import Gateway
from pyftg.utils.logging import DEBUG, set_logging
from problogAgent.problog_agent import ProblogAgent


# Utilizzo di `typer` per gestire i comandi
app = typer.Typer(pretty_exceptions_enable=False)


# Funzione principale per avviare il gioco
async def start_process(
    host: str,
    port: int,
    keyboard: bool = False,
    problog: bool = False,
    character: str = "ZEN",
    game_num: int = 1,
):
    # Creazione del gateway per connettersi a DareFightingICE
    gateway = Gateway(host, port)
    
    # Inizializzazione degli agenti
    agent1 = KickAI()
    agent2 = DisplayInfo()
    agent3 = ProblogAgent(knowledge_base_path="knowledge_base.pl")
    print("Questo è un messaggio di log")


    # Registrazione degli agenti con il gateway
    gateway.register_ai("DisplayInfo", agent2)
    if keyboard:
        print("Questo è un messaggio di log keyboard")
        await gateway.run_game(
            [character, character], ["Keyboard", "DisplayInfo"], game_num
        )
    elif problog:
        print("Questo è un messaggio di log problog")
        gateway.register_ai("ProblogAgent", agent3)
        await gateway.run_game(
            [character, character], ["ProblogAgent", "DisplayInfo"], game_num
        )
    else:
        print("Questo è un messaggio di log prosciutto")
        gateway.register_ai("KickAI", agent1)
        await gateway.run_game(
            [character, character], ["KickAI", "DisplayInfo"], game_num
        )
    


# Comando CLI per avviare il processo
@app.command()
def main(
    host: Annotated[
        Optional[str], typer.Option(help="Host usato da DareFightingICE")
    ] = "127.0.0.1",  # Host predefinito
    port: Annotated[
        Optional[int], typer.Option(help="Porta usata da DareFightingICE")
    ] = 31415,  # Porta predefinita
    keyboard: Annotated[bool, typer.Option(help="Usa la tastiera per giocare")] = False,
    problog: Annotated[bool, typer.Option(help="Fai giocare un agente basato su problog")] = False,
):
    # Avvio del gioco utilizzando asyncio
    asyncio.run(start_process(host, port, keyboard, problog))


# Entry point
if __name__ == "__main__":
    set_logging(log_level=DEBUG)
    app()
