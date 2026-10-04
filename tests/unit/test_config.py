"""
Tests for Wakapi MCP server configuration management
"""

import sys
import os
import tempfile
import inspect
from pathlib import Path
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / ".." / ".." / "src"))

# Remove any cached modules
if 'wakapi_sdk.core.config' in sys.modules:
    del sys.modules['wakapi_sdk.core.config']
if "wakapi_sdk_project.src.wakapi_sdk.core.config" in sys.modules:
    del sys.modules["wakapi_sdk_project.src.wakapi_sdk.core.config"]

from wakapi_sdk.core.config import ConfigManager

# Reset ConfigManager instance before each test
def setup_function():
    ConfigManager._reset_instance()

# Debug: Print ConfigManager __init__ signature
print(f"ConfigManager.__init__ signature: {inspect.signature(ConfigManager.__init__)}")


class TestConfigManager:
    """Tests for ConfigManager"""

    def test_load_from_wakatime_config_basic(self):
        """Basic wakatime.cfg loading works correctly"""
        # Force reset and create new instance
        ConfigManager._reset_instance()

        # Create temporary wakatime.cfg file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write("""[settings]
api_key = test-api-key
api_url = http://localhost:3000/api
""")
            wakatime_config_path = Path(f.name)

        try:
            config_manager = ConfigManager(wakatime_config_path=wakatime_config_path)
            wakapi_config = config_manager.get_wakapi_config()

            # Check that api_key is loaded correctly
            assert wakapi_config.api_key == "test-api-key"

            # Check that api_url is loaded and /api is removed for internal use
            assert wakapi_config.url == "http://localhost:3000"
        finally:
            # Clean up temporary file
            os.unlink(wakatime_config_path)

    def test_load_from_wakatime_config_without_api_suffix(self):
        """Wakatime.cfg loading works correctly when api_url doesn't end with /api"""
        # Force reset and create new instance
        ConfigManager._reset_instance()

        # Create temporary wakatime.cfg file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write("""[settings]
api_key = test-api-key
api_url = http://localhost:3000
""")
            wakatime_config_path = Path(f.name)

        try:
            # Force reset and create new instance
            ConfigManager._reset_instance()
            config_manager = ConfigManager(wakatime_config_path=wakatime_config_path)
            wakapi_config = config_manager.get_wakapi_config()

            # Check that api_key is loaded correctly
            assert wakapi_config.api_key == "test-api-key"

            # Check that api_url is loaded as is
            assert wakapi_config.url == "http://localhost:3000"
        finally:
            # Clean up temporary file
            os.unlink(wakatime_config_path)

    def test_check_duplicate_config_url(self):
        """Duplicate configuration check works for WAKAPI_URL"""
        # Reset ConfigManager instance before test
        ConfigManager._reset_instance()

        # Create temporary config file (TOML)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("""[wakapi]
url = "http://localhost:3000"
api_key = "toml-api-key"
""")
            config_path = Path(f.name)

        # Create temporary wakatime.cfg file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write("""[settings]
api_key = cfg-api-key
api_url = http://localhost:3000/api
""")
            wakatime_config_path = Path(f.name)

        try:
            # Reset ConfigManager instance before test
            ConfigManager._reset_instance()
            # Should not raise ConfigurationError anymore as duplicates are now allowed
            # Instead, it should use the config file value (takes precedence over wakatime.cfg)
            config_manager = ConfigManager(
                config_path=Path(config_path),
                wakatime_config_path=Path(wakatime_config_path),
            )
            wakapi_config = config_manager.get_wakapi_config()

            # Should use values from config file (takes precedence over wakatime.cfg)
            assert wakapi_config.api_key == "toml-api-key"
            assert wakapi_config.url == "http://localhost:3000"
        finally:
            # Clean up temporary files
            os.unlink(config_path)
            os.unlink(wakatime_config_path)

    def test_env_var_precedence(self):
        """Environment variables take precedence over config files and wakatime.cfg"""
        # Reset ConfigManager instance before test
        ConfigManager._reset_instance()

        # Create temporary config file (TOML)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("""[wakapi]
url = "http://localhost:3000"
api_key = "toml-api-key"
""")
            config_path = Path(f.name)

        # Create temporary wakatime.cfg file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write("""[settings]
api_key = cfg-api-key
api_url = http://localhost:3000/api
""")
            wakatime_config_path = Path(f.name)

        try:
            # Set environment variables
            os.environ['WAKAPI_URL'] = 'http://env-var-url:3000'
            os.environ['WAKAPI_API_KEY'] = 'env-api-key'

            # Should not raise any error
            config_manager = ConfigManager(config_path=Path(config_path), wakatime_config_path=Path(wakatime_config_path))
            wakapi_config = config_manager.get_wakapi_config()

            # Should use values from environment variables (takes highest precedence)
            assert wakapi_config.api_key == "env-api-key"
            assert wakapi_config.url == "http://env-var-url:3000"
        finally:
            # Clean up temporary files
            os.unlink(config_path)
            os.unlink(wakatime_config_path)
            # Clean up environment variables
            if 'WAKAPI_URL' in os.environ:
                del os.environ['WAKAPI_URL']
            if 'WAKAPI_API_KEY' in os.environ:
                del os.environ['WAKAPI_API_KEY']

    def test_config_file_precedence_over_wakatime_cfg(self):
        """Config file takes precedence over wakatime.cfg"""
        # Reset ConfigManager instance before test
        ConfigManager._reset_instance()

        # Create temporary config file (TOML)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("""[wakapi]
url = "http://localhost:3000"
api_key = "toml-api-key"
""")
            config_path = Path(f.name)

        # Create temporary wakatime.cfg file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write("""[settings]
api_key = cfg-api-key
api_url = http://localhost:3000/api
""")
            wakatime_config_path = Path(f.name)

        try:
            # Should not raise any error
            config_manager = ConfigManager(config_path=Path(config_path), wakatime_config_path=Path(wakatime_config_path))
            wakapi_config = config_manager.get_wakapi_config()

            # Should use values from config file (takes precedence over wakatime.cfg)
            assert wakapi_config.api_key == "toml-api-key"
            assert wakapi_config.url == "http://localhost:3000"
        finally:
            # Clean up temporary files
            os.unlink(config_path)
            os.unlink(wakatime_config_path)

    def test_check_duplicate_config_api_key(self):
        """Config file takes precedence over wakatime.cfg for WAKAPI_API_KEY"""
        # Reset ConfigManager instance before test
        ConfigManager._reset_instance()

        # Create temporary config file (TOML)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("""[wakapi]
url = "http://localhost:3000"
api_key = "toml-api-key"
""")
            config_path = Path(f.name)

        # Create temporary wakatime.cfg file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write("""[settings]
api_key = cfg-api-key
api_url = http://localhost:3000/api
""")
            wakatime_config_path = Path(f.name)

        try:
            # Should not raise ConfigurationError anymore as duplicates are now allowed
            # Instead, it should use the config file value (takes precedence over wakatime.cfg)
            config_manager = ConfigManager(config_path=Path(config_path), wakatime_config_path=Path(wakatime_config_path))
            wakapi_config = config_manager.get_wakapi_config()

            # Should use values from config file (takes precedence over wakatime.cfg)
            assert wakapi_config.api_key == "toml-api-key"
            assert wakapi_config.url == "http://localhost:3000"
        finally:
            # Clean up temporary files
            os.unlink(config_path)
            os.unlink(wakatime_config_path)

    def test_check_duplicate_config_both(self):
        """Config file takes precedence over wakatime.cfg for both WAKAPI_URL and WAKAPI_API_KEY"""
        # Reset ConfigManager instance before test
        ConfigManager._reset_instance()

        # Create temporary config file (TOML)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("""[wakapi]
url = "http://localhost:3000"
api_key = "toml-api-key"
""")
            config_path = Path(f.name)

        # Create temporary wakatime.cfg file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write("""[settings]
api_key = cfg-api-key
api_url = http://localhost:3000/api
""")
            wakatime_config_path = Path(f.name)

        try:
            # Should not raise ConfigurationError anymore as duplicates are now allowed
            # Instead, it should use the config file values (takes precedence over wakatime.cfg)
            config_manager = ConfigManager(config_path=Path(config_path), wakatime_config_path=Path(wakatime_config_path))
            wakapi_config = config_manager.get_wakapi_config()

            # Should use values from config file (takes precedence over wakatime.cfg)
            assert wakapi_config.api_key == "toml-api-key"
            assert wakapi_config.url == "http://localhost:3000"
        finally:
            # Clean up temporary files
            os.unlink(config_path)
            os.unlink(wakatime_config_path)

    def test_wakatime_cfg_fallback(self):
        """Wakatime.cfg values are used when no other config sources provide them"""
        # Reset ConfigManager instance before test
        ConfigManager._reset_instance()

        # Create temporary config file (TOML) without api_key
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("""[wakapi]
url = "http://localhost:3000"
""")
            config_path = Path(f.name)

        # Create temporary wakatime.cfg file with api_key
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write("""[settings]
api_key = cfg-api-key
debug = false
hidefilenames = false
api_url = http://localhost:3000/api
""")
            wakatime_config_path = Path(f.name)

        try:
            # Should not raise any error
            config_manager = ConfigManager(config_path=Path(config_path), wakatime_config_path=Path(wakatime_config_path))
            wakapi_config = config_manager.get_wakapi_config()

            # Should use url from config file and api_key from wakatime.cfg
            assert wakapi_config.api_key == "cfg-api-key"
            assert wakapi_config.url == "http://localhost:3000"
        finally:
            # Clean up temporary files
            os.unlink(config_path)
            os.unlink(wakatime_config_path)

    def test_load_from_default_wakatime_cfg_location(self):
        """Test loading from default wakatime.cfg file location"""
        # Reset ConfigManager instance before test
        ConfigManager._reset_instance()

        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)

            # Create wakatime.cfg file in the temporary directory
            wakatime_cfg_path = temp_dir_path / "wakatime.cfg"
            with open(wakatime_cfg_path, 'w') as f:
                f.write("""[settings]
api_key = test-default-api-key
api_url = http://default-server:3000/api
""")

            # Save current working directory
            original_cwd = os.getcwd()

            try:
                # Change working directory to the temporary directory
                os.chdir(temp_dir_path)

                # Load config using default location (should find wakatime.cfg in current directory)
                config_manager = ConfigManager(wakatime_config_path=Path("wakatime.cfg"))
                wakapi_config = config_manager.get_wakapi_config()

                # Assert that the config was loaded correctly
                assert wakapi_config.api_key == "test-default-api-key"
                assert wakapi_config.url == "http://default-server:3000"

            finally:
                # Restore original working directory
                os.chdir(original_cwd)

    def test_api_url_processing(self):
        """Test that URL processing removes '/api' suffix correctly"""
        # Reset ConfigManager instance before test
        ConfigManager._reset_instance()

        # Test case 1: URL with /api suffix should have it removed
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write("""[settings]
api_key = test-api-key-1
api_url = https://example.com/api
""")
            wakatime_config_path_with_api = Path(f.name)

        try:
            config_manager_with_api = ConfigManager(wakatime_config_path=wakatime_config_path_with_api)
            wakapi_config_with_api = config_manager_with_api.get_wakapi_config()

            # Assert /api suffix is removed
            assert wakapi_config_with_api.url == "https://example.com"
            assert wakapi_config_with_api.api_key == "test-api-key-1"
        finally:
            # Clean up temporary file
            os.unlink(wakatime_config_path_with_api)

        # Reset ConfigManager instance for second test
        ConfigManager._reset_instance()

        # Test case 2: URL without /api suffix should remain unchanged
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write("""[settings]
api_key = test-api-key-2
api_url = https://example.com
""")
            wakatime_config_path_without_api = Path(f.name)

        try:
            config_manager_without_api = ConfigManager(wakatime_config_path=wakatime_config_path_without_api)
            wakapi_config_without_api = config_manager_without_api.get_wakapi_config()

            # Assert URL remains unchanged
            assert wakapi_config_without_api.url == "https://example.com"
            assert wakapi_config_without_api.api_key == "test-api-key-2"
        finally:
            # Clean up temporary file
            os.unlink(wakatime_config_path_without_api)

    def test_priority_order(self):
        """Test configuration priority order: environment variables > current format > wakatime.cfg"""
        # Reset ConfigManager instance before test
        ConfigManager._reset_instance()

        # Test 1: Environment variables should take highest precedence
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write("""[settings]
api_key = cfg_key
api_url = https://cfg.com/api
""")
            wakatime_config_path = Path(f.name)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("""[wakapi]
url = "https://dict.com"
api_key = "dict_key"
""")
            config_path = Path(f.name)

        try:
            os.environ['WAKAPI_API_KEY'] = 'env_key'
            os.environ['WAKAPI_URL'] = 'https://env.com'

            config_manager = ConfigManager(config_path=config_path, wakatime_config_path=wakatime_config_path)
            wakapi_config = config_manager.get_wakapi_config()

            # Assert final config uses env values
            assert wakapi_config.api_key == "env_key"
            assert wakapi_config.url == "https://env.com"
        finally:
            os.unlink(config_path)
            os.unlink(wakatime_config_path)
            if 'WAKAPI_API_KEY' in os.environ:
                del os.environ['WAKAPI_API_KEY']
            if 'WAKAPI_URL' in os.environ:
                del os.environ['WAKAPI_URL']

        # Reset ConfigManager instance for next test
        ConfigManager._reset_instance()

        # Test 2: With env vars unset, dict should override cfg
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write("""[settings]
api_key = cfg_key
api_url = https://cfg.com/api
""")
            wakatime_config_path = Path(f.name)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("""[wakapi]
url = "https://dict.com"
api_key = "dict_key"
""")
            config_path = Path(f.name)

        try:
            config_manager = ConfigManager(config_path=config_path, wakatime_config_path=wakatime_config_path)
            wakapi_config = config_manager.get_wakapi_config()

            # Assert dict values override cfg values
            assert wakapi_config.api_key == "dict_key"
            assert wakapi_config.url == "https://dict.com"
        finally:
            os.unlink(config_path)
            os.unlink(wakatime_config_path)

        # Reset ConfigManager instance for next test
        ConfigManager._reset_instance()

        # Test 3: With both env and dict unset, cfg values should be used
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write("""[settings]
api_key = cfg_key
api_url = https://cfg.com/api
""")
            wakatime_config_path = Path(f.name)

        try:
            # Create config manager without config_path (no dict format)
            config_manager = ConfigManager(wakatime_config_path=wakatime_config_path)
            wakapi_config = config_manager.get_wakapi_config()

            # Assert cfg values are used
            assert wakapi_config.api_key == "cfg_key"
            assert wakapi_config.url == "https://cfg.com"
        finally:
            os.unlink(wakatime_config_path)

    def test_mapping_correctness(self):
        """Test correct mapping of api_key and api_url from wakatime.cfg"""
        # Clean up environment variables that might be set by other tests
        env_vars_to_clean = ['WAKAPI_API_KEY', 'WAKAPI_URL', 'WAKAPI_API_PATH', 'DEBUG']
        original_env = {}
        for var in env_vars_to_clean:
            if var in os.environ:
                original_env[var] = os.environ[var]
                del os.environ[var]

        # Reset ConfigManager instance before test
        ConfigManager._reset_instance()

        # Create temporary wakatime.cfg file with [settings] section and [ignored_section]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write("""[settings]
api_key = mapped_key
api_url = https://mapped.com/api
additional_key = ignored_value

[ignored_section]
api_key = wrong_key
""")
            wakatime_config_path = Path(f.name)

        try:
            config_manager = ConfigManager(wakatime_config_path=wakatime_config_path)
            wakapi_config = config_manager.get_wakapi_config()

            # Debug: Print config manager state
            print("DEBUG: ConfigManager state:")

            # Assert api_key is loaded correctly from [settings] section
            assert wakapi_config.api_key == "mapped_key", \
                f"Expected 'mapped_key' but got '{wakapi_config.api_key}'. " \
                f"Check if wakatime.cfg is being read correctly: {wakatime_config_path}"

            # Assert api_url is loaded and /api is removed for internal use
            assert wakapi_config.url == "https://mapped.com"

            # Assert additional_key is not loaded as it's not a recognized config key
            # We check that the WakapiConfig object doesn't have this attribute
            # Note: Since additional_key is not mapped to any WakapiConfig field,
            # it won't be accessible through the config object
            # The test is implicitly checking that only mapped keys are used

            # Assert api_key is not loaded from [ignored_section]
            assert wakapi_config.api_key != "wrong_key"
        finally:
            # Clean up temporary file
            os.unlink(wakatime_config_path)
            # Restore original environment variables
            for var in env_vars_to_clean:
                if var in os.environ:
                    del os.environ[var]
            for var, value in original_env.items():
                os.environ[var] = value
            # Reset ConfigManager instance after test
            ConfigManager._reset_instance()

    def test_load_from_wakatime_config_vault_command(self):
        """Vault command functionality works correctly"""
        # Create temporary wakatime.cfg file with vault command
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cfg", delete=False) as f:
            f.write("""[settings]
api_key_vault_cmd = echo "vault-api-key"
api_url = http://localhost:3000/api
""")
            wakatime_config_path = Path(f.name)

        try:
            # Force reset and create new instance
            ConfigManager._reset_instance()
            config_manager = ConfigManager(wakatime_config_path=wakatime_config_path)
            wakapi_config = config_manager.get_wakapi_config()

            # Check that vault command API key is loaded correctly
            assert wakapi_config.api_key == "vault-api-key"
            # Check that api_url is loaded correctly
            assert wakapi_config.url == "http://localhost:3000"
        finally:
            # Clean up temporary file
            os.unlink(wakatime_config_path)

    def test_load_from_wakatime_config_vault_command_fallback(self):
        """Vault command fallback to regular api_key when vault fails"""
        # Create temporary wakatime.cfg file with failing vault command
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cfg", delete=False) as f:
            f.write("""[settings]
api_key_vault_cmd = non_existent_command
api_key = fallback-api-key
api_url = http://localhost:3000/api
""")
            wakatime_config_path = Path(f.name)

        try:
            # Force reset and create new instance
            ConfigManager._reset_instance()
            config_manager = ConfigManager(wakatime_config_path=wakatime_config_path)
            wakapi_config = config_manager.get_wakapi_config()

            # Check that fallback API key is used when vault command fails
            assert wakapi_config.api_key == "fallback-api-key"
        finally:
            # Clean up temporary file
            os.unlink(wakatime_config_path)
            # Force reset again to ensure clean state
            ConfigManager._reset_instance()

    def test_load_from_wakatime_config_vault_precedence(self):
        """Vault command takes precedence over regular api_key"""
        # Create temporary wakatime.cfg file with both vault command and api_key
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cfg", delete=False) as f:
            f.write("""[settings]
api_key_vault_cmd = echo "vault-key"
api_key = regular-key
api_url = http://localhost:3000/api
""")
            wakatime_config_path = Path(f.name)

        try:
            # Force reset and create new instance
            ConfigManager._reset_instance()
            config_manager = ConfigManager(wakatime_config_path=wakatime_config_path)
            wakapi_config = config_manager.get_wakapi_config()

            # Check that vault command API key takes precedence
            assert wakapi_config.api_key == "vault-key"
        finally:
            # Clean up temporary file
            os.unlink(wakatime_config_path)
            # Force reset again to ensure clean state
            ConfigManager._reset_instance()