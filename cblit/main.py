import typer
from rich import print

from cblit.gpt.country import ConstructedCountrySession

app = typer.Typer(pretty_exceptions_show_locals=False)


@app.callback()
def cli() -> None:
    """Cosmic Bureaucracy: Lost in Translation"""
    pass


@app.command()
def start() -> None:
    """Start game command"""
    country_session = ConstructedCountrySession()
    print(country_session.chat)
    print(country_session.country)
    # chat = ChatSession()
    while(True):
        user_message = typer.prompt(">")
        gpt_response = country_session.from_english(user_message)
        print(country_session.chat.to_list())
        print(f"<: {gpt_response}")

    pass


if __name__ == "__main__":
    app()
