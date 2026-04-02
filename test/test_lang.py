from unittest.mock import (
    patch,
    mock_open,
    MagicMock,
)

import json

from lang.translator import (
    Translator,
)

class TestLangModule:
    class TestTranslator:
        def test_instance(self):
            """ Test that an instance of Translator can be created and that it initializes the _data attribute as an empty dictionary. """

            translator = Translator()

            assert translator is not None
            assert translator._data == {}

        def test_instance_auto_repair(self):
            """ Test that if the keys module cannot be imported, the Translator instance will attempt to generate keys and then import successfully. """

            with patch("lang.translator.Translator.generate_keys") as mock_gen:
                from lang.translator import Translator
                with patch("builtins.__import__", side_effect=[ImportError, MagicMock()]):
                    Translator()
                    mock_gen.assert_called()

        def test_load_files(self):
            """ Test that the load method correctly reads translation files from the specified directory and populates the _data attribute. """

            with patch("os.listdir", return_value=["en.json", "es.json", "invalid.txt"]):
                mock_data_en = json.dumps({"test": "hello"})
                mock_data_es = json.dumps({"test": "hola"})
                
                with patch("builtins.open", mock_open()) as mocked_file:
                    mocked_file.side_effect = [
                        mock_open(read_data=mock_data_en).return_value,
                        mock_open(read_data=mock_data_es).return_value
                    ]
                    
                    translator = Translator()
                    translator.load()

            assert "en" in translator._data
            assert "es" in translator._data
            assert translator._data["en"]["test"] == "hello"
            assert translator._data["es"]["test"] == "hola"

        def test_translation_basic(self):
            """ Test that the t method returns the correct translation for a given key and language. """

            translator = Translator()
            translator._data = {
                "en": {
                    "cmds": {
                        "ping": "Pong!"
                    }
                }
            }

            assert translator.t("en", "cmds.ping") == "Pong!"

        def test_translation_not_found(self):
            """ Test that the t method returns a default message when a translation is not found. """

            translator = Translator()
            translator._data = {"en": {"a": "b"}}
            result = translator.t("en", "missing.key")

            assert result == "[missing.key?!]"

        def test_translation_with_placeholders(self):
            """ Test that the t method correctly formats translations with placeholders. """

            translator = Translator()
            translator._data = {
                "en": {
                    "welcome": "Hello {name}!"
                }
            }

            assert translator.t("en", "welcome", name="Lucy") == "Hello Lucy!"

        def test_translation_with_list(self):
            """ Test that the t method correctly formats translations with lists. """

            translator = Translator()
            translator._data = {
                "en": {
                    "steps": ["Step 1", "Step 2"]
                }
            }

            assert translator.t("en", "steps") == "Step 1\nStep 2"

        def test_generate_keys(self):
            """ Test that the generate_keys method creates a keys.py file with the correct structure based on the loaded translation data. """

            translator = Translator()
            translator._data = {
                "en": {
                    "simple": "val",
                    "nested": {
                        "key": "val2"
                    }
                }
            }
            
            with (
                patch("os.path.join", return_value="dummy_path/keys.py"),
                patch("builtins.open", mock_open()) as mocked_file
            ):
                with patch.object(translator, 'load'):
                    translator.generate_keys()
                    mocked_file.assert_called_once()
                    
                    handle = mocked_file()
                    written_content = "".join(call.args[0] for call in handle.write.call_args_list)
                    
                    assert "class K:" in written_content
                    assert "simple = \"simple\"" in written_content
                    assert "class nested:" in written_content
                    assert "key = \"nested.key\"" in written_content

        def test_generate_keys_with_lists(self):
            """ Test that the generate_keys method correctly handles lists in the translation data when creating keys.py. """

            translator = Translator()
            translator._data = {
                "en": {
                    "steps": [
                        {"desc": "step 1"},
                        "simple step"
                    ]
                }
            }
            
            with (
                patch("os.path.join", return_value="dummy_path/keys.py"),
                patch("builtins.open", mock_open()) as mocked_file
            ):
                with patch.object(translator, 'load'):
                    translator.generate_keys()
                    
                    handle = mocked_file()
                    content = "".join(call.args[0] for call in handle.write.call_args_list)
                    
                    assert "class steps:" in content
                    assert "class _0:" in content
                    assert "desc = \"steps.0.desc\"" in content
                    assert "_1 = \"steps.1\"" in content
