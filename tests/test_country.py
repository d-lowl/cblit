from cblit.gpt.country import format_translation_prompt


def test_format_translation_prompt():
    expected_prompt = "Translate from Test to Navi: Hello. Give your answer in this format \"Translation: X\". Avoid " \
                      "providing unnecessary details. If you think there\'s no translation, respond with: " \
                      "\"Translation: []\""

    prompt = format_translation_prompt("Test", "Navi", "Hello")

    assert expected_prompt == prompt
