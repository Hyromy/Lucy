from unittest.mock import (
    MagicMock,
    patch,
)

from utils.funcs import (
    normalize_url,
    id_url_param,
    get_cogs_dict,
    get_bot_info,
)

from utils.logger import (
    DateRotatingFileHandler,
)

class TestUtilsModule:
    class TestFuncs:
        def test_normalize_url(self):
            """ Test that normalize_url correctly constructs a URL from a base and endpoint, and handles trailing slashes as expected. """

            assert (
                normalize_url("https://api.com", "user")
                == "https://api.com/user/"
            )
            assert (
                normalize_url("https://api.com/", "/user/")
                == "https://api.com/user/"
            )
            assert (
                normalize_url("https://api.com", "user", trailing_slash = False)
                == "https://api.com/user"
            )
            assert (
                normalize_url("https://api.com/v1", "test")
                == "https://api.com/v1/test/"
            )

        def test_id_url_param(self):
            """ Test that id_url_param correctly converts valid integer IDs to strings and returns an empty string for invalid inputs. """

            assert id_url_param(123) == "123"
            assert id_url_param(0) == ""
            assert id_url_param(-1) == ""
            assert id_url_param("123") == ""

        def test_get_cogs_dict(self):
            """ Test that get_cogs_dict correctly generates a dictionary of cog information from a mock Lucy instance. """

            mock_cog = MagicMock()
            mock_cog.__cog_name__ = "General"
            mock_cog.show = True
            mock_cog.icon = "🏠"
            
            mock_cmd = MagicMock()
            mock_cmd.name = "ping"
            mock_cog.get_app_commands.return_value = [mock_cmd]
            
            mock_lucy = MagicMock()
            mock_lucy.cogs = {"General": mock_cog}
            
            result = get_cogs_dict(mock_lucy)
            
            assert "General" in result
            assert result["General"]["name"] == "general"
            assert result["General"]["show"]
            assert "ping" in result["General"]["app_commands"]

        def test_get_bot_info(self):
            """ Test that get_bot_info correctly extracts information from a mock Lucy instance. """

            mock_lucy = MagicMock()
            mock_lucy.user.name = "LucyBot"
            mock_lucy.user.display_avatar.url = "http://avatar.com"
            mock_lucy.OWNER.name = "Owner"
            mock_lucy.OWNER.display_avatar.url = "http://owner.com"
            mock_lucy.VERSION = "2.0.0"
            mock_lucy.cache.get.return_value = {"help": 1}
            
            info = get_bot_info(mock_lucy)
            
            assert info["bot_name"] == "LucyBot"
            assert info["version"] == "2.0.0"
            assert info["slash_cmds_cache"] == {"help": 1}

    class TestLogger:
        def test_handler_instance(self):
            """ Test that a DateRotatingFileHandler instance can be created with the specified maxBytes and that it has the expected attributes. """

            with patch("builtins.open", MagicMock()):
                handler = DateRotatingFileHandler("test.log", maxBytes = 100)
                assert handler.maxBytes == 100

        def test_should_rollover(self):
            """ Test that the shouldRollover method returns True when the log file exceeds the specified maxBytes. """

            with (
                patch("os.path.exists", return_value = True),
                patch("os.path.getsize", return_value = 150),
                patch("builtins.open", MagicMock())
            ):
                
                handler = DateRotatingFileHandler("test.log", maxBytes = 100)
                assert handler.shouldRollover() is True

        def test_do_rollover(self):
            """ Test that the doRollover method renames the current log file with a timestamp and creates a new log file. """

            with (
                patch("os.rename") as mock_rename,
                patch("os.path.exists", return_value = True),
                patch("builtins.open", MagicMock())
            ):
                
                handler = DateRotatingFileHandler("test.log")
                handler.doRollover()
                
                assert mock_rename.called
                assert "lucy-" in mock_rename.call_args[0][1]
