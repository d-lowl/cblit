"""Traslator wrapper runner."""
import asyncio

from cblit.cli.session_wrapper import SessionWrapper
from cblit.session.translator import ConlangEntry, TranslatorSession


async def wrap_translator() -> None:
    """Create translator session, wrap and run."""
    translator = TranslatorSession(
        "Kori",
        ConlangEntry(english="The flowers are blooming in the meadow.", conlang="Prec na ca ceh tiôplox.")
    )
    wrapper = SessionWrapper.from_session(translator)
    await wrapper.run()

if __name__ == "__main__":
    asyncio.run(wrap_translator())
