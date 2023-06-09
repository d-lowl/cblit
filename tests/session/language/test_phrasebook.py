"""Phrasebook tests."""
from collections.abc import Iterator
from unittest.mock import MagicMock, call, patch

import pytest

from cblit.session.language.phrasebook import Phrasebook
from cblit.session.language.translator import ConlangEntry, TranslatorSession

MODULE_PATH = "cblit.session.language.phrasebook"
TWO_CALLS = 2

@pytest.fixture
def mock_translator_session() -> Iterator[MagicMock]:
    """Mock Translator Session.

    Always translates in a form of "translated {phrase}"

    Yields:
        MagicMock: mocked translator session instance
    """

    async def mock_translate(from_language: str, to_language: str, phrase: str) -> ConlangEntry:
        """Mock translation.

        Always translates in a form of "translated {phrase}"

        Args:
            from_language (str): unused
            to_language (str): unused
            phrase (str): phrase to translate

        Returns:
            ConlangEntry:
        """
        return ConlangEntry(
            english=phrase,
            conlang=f"translated {phrase}"
        )

    with patch(f"{MODULE_PATH}.TranslatorSession") as mock_translator_session_class:
        mock_translator_session_instance = mock_translator_session_class.return_value
        mock_translator_session_instance.conlang_name = "testlang"
        mock_translator_session_instance.translate.side_effect = mock_translate
        yield mock_translator_session_instance


@pytest.mark.asyncio
async def test_from_translator_session(mock_translator_session: TranslatorSession):
    """Test initialisation of phrasebook with Translator Session.

    Args:
        mock_translator_session (TranslatorSession): mock translator session instance
    """
    expected_phrasebook = Phrasebook(
        phrases=[
            ConlangEntry(english="phrase1", conlang="translated phrase1"),
            ConlangEntry(english="phrase2", conlang="translated phrase2"),
        ]
    )

    phrasebook = await Phrasebook.from_translator_session(
        mock_translator_session,
        ["phrase1", "phrase2"]
    )

    assert call("English", "testlang", "phrase1") in mock_translator_session.translate.call_args_list
    assert call("English", "testlang", "phrase2") in mock_translator_session.translate.call_args_list
    assert mock_translator_session.translate.call_count == TWO_CALLS
    assert phrasebook == expected_phrasebook
