import os
import tempfile
import pytest
import requests_mock
import json
from unittest.mock import patch, mock_open

# Import the script to test
import zed_backup


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.fixture
def mock_env_setup():
    """Mock environment setup."""
    env_vars = {
        "GITHUB_TOKEN": "test_github_token",
        "FILE_TO_UPLOAD": "/path/to/settings.json",
    }

    with patch.dict(os.environ, env_vars):
        with patch("zed_backup.GITHUB_TOKEN", "test_github_token"):
            with patch("zed_backup.FILE_TO_UPLOAD", "/path/to/settings.json"):
                yield


class TestGistOperations:
    """Test Gist operations."""

    @pytest.fixture
    def sample_content(self):
        return '{"setting": "value"}'

    @pytest.fixture
    def mock_file_read(self, sample_content):
        """Mock file reading."""
        return patch("builtins.open", mock_open(read_data=sample_content))

    def test_create_gist_success(self, mock_env_setup, mock_file_read, sample_content):
        """Test successful Gist creation."""
        gist_id = "test_gist_id"
        gist_url = "https://gist.github.com/test_gist_id"

        with requests_mock.Mocker() as m:
            m.post(
                zed_backup.GITHUB_API_URL,
                json={"id": gist_id, "html_url": gist_url},
                status_code=201,
            )

            with (
                mock_file_read,
                patch("builtins.print") as mock_print,
                patch("os.path.basename", return_value="settings.json"),
            ):
                zed_backup.create_gist()

                # Verify API call
                request = m.request_history[0]
                assert request.method == "POST"
                body = json.loads(request.text)
                assert body["public"] == False
                assert "settings.json" in body["files"]
                assert body["files"]["settings.json"]["content"] == sample_content

                # Verify output
                mock_print.assert_any_call("Created gist with id:", gist_id)
                mock_print.assert_any_call("Gist URL:", gist_url)

    def test_create_gist_error(self, mock_env_setup, mock_file_read):
        """Test Gist creation with API error."""
        with requests_mock.Mocker() as m:
            m.post(
                zed_backup.GITHUB_API_URL,
                json={"message": "Bad credentials"},
                status_code=401,
            )

            with mock_file_read, patch("builtins.print") as mock_print:
                zed_backup.create_gist()

                mock_print.assert_called_with(
                    "Error creating gist:", 401, '{"message": "Bad credentials"}'
                )

    def test_update_gist_success(self, mock_env_setup, mock_file_read, sample_content):
        """Test successful Gist update."""
        gist_id = "existing_gist_id"
        gist_url = "https://gist.github.com/existing_gist_id"

        with requests_mock.Mocker() as m:
            m.patch(
                f"{zed_backup.GITHUB_API_URL}/{gist_id}",
                json={"html_url": gist_url},
                status_code=200,
            )

            with (
                mock_file_read,
                patch("builtins.print") as mock_print,
                patch("os.path.basename", return_value="settings.json"),
            ):
                zed_backup.update_gist(gist_id)

                # Verify API call
                request = m.request_history[0]
                assert request.method == "PATCH"
                body = json.loads(request.text)
                assert "settings.json" in body["files"]
                assert body["files"]["settings.json"]["content"] == sample_content

                # Verify output
                mock_print.assert_any_call("Updated gist", gist_id)
                mock_print.assert_any_call("Gist URL:", gist_url)

    def test_update_gist_error(self, mock_env_setup, mock_file_read):
        """Test Gist update with API error."""
        gist_id = "invalid_gist_id"

        with requests_mock.Mocker() as m:
            m.patch(
                f"{zed_backup.GITHUB_API_URL}/{gist_id}",
                json={"message": "Not Found"},
                status_code=404,
            )

            with mock_file_read, patch("builtins.print") as mock_print:
                zed_backup.update_gist(gist_id)

                mock_print.assert_called_with(
                    "Error updating gist:", 404, '{"message": "Not Found"}'
                )


class TestMainFunction:
    """Test the main function."""

    def test_main_create_new_gist(self, mock_env_setup):
        """Test main function when no gist ID file exists."""
        with (
            patch("os.path.exists", return_value=False),
            patch("zed_backup.create_gist") as mock_create_gist,
        ):
            zed_backup.main()
            mock_create_gist.assert_called_once()

    def test_main_update_existing_gist(self, mock_env_setup):
        """Test main function when gist ID file exists with an ID."""
        gist_id = "existing_gist_id"

        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=gist_id)),
            patch("zed_backup.update_gist") as mock_update_gist,
        ):
            zed_backup.main()
            mock_update_gist.assert_called_once_with(gist_id)

    def test_main_empty_gist_id_file(self, mock_env_setup):
        """Test main function when gist ID file exists but is empty."""
        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data="")),
            patch("zed_backup.create_gist") as mock_create_gist,
        ):
            zed_backup.main()
            mock_create_gist.assert_called_once()


class TestEnvironmentSetup:
    """Test environment setup."""

    def test_missing_github_token(self):
        """Test that the script raises an exception when GITHUB_TOKEN is not set."""
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("os.getenv", return_value=None),
            patch("zed_backup.GITHUB_TOKEN", None),
        ):
            with pytest.raises(Exception) as exc_info:
                # Just importing the module again should trigger the exception
                from importlib import reload

                reload(zed_backup)

            assert "GITHUB_TOKEN is not set" in str(exc_info.value)
