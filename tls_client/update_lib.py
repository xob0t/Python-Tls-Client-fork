from __future__ import annotations  # Enable forward references for type hints.

import os  # Import the 'os' module for interacting with the operating system.
from datetime import datetime, timedelta, timezone  # Import specific classes from the 'datetime' module for working with dates and times.
from typing import Any, Dict, Optional  # Import type hinting utilities for better code readability and maintainability.

import requests  # Import the 'requests' library for making HTTP requests.

from .utils import get_dependency_filename  # Import a function from the local 'utils' module, likely used to determine the filename of a dependency.

GITHUB_API_URL = "https://api.github.com/repos/bogdanfinn/tls-client/releases/latest"  # Define the URL for the GitHub API endpoint to fetch the latest release information.
LOCAL_VERSION_FILE = os.path.join(os.path.dirname(__file__), "dependencies/version.txt")  # Construct the path to a local file where the currently installed version is stored.
DOWNLOAD_DIR = os.path.dirname(LOCAL_VERSION_FILE)  # Determine the directory where dependencies are downloaded, based on the location of the version file.
CHECK_INTERVAL = timedelta(hours=24)  # Define the interval after which to check for updates (24 hours in this case).

CURRENT_DEPENDENCY_FILENAME = get_dependency_filename()  # Get the filename of the current dependency using the imported utility function.


def get_latest_release(session: requests.Session) -> tuple[Any, str | None] | None:
    """Fetches the latest release information from GitHub, using conditional requests if possible."""
    headers = {}  # Initialize an empty dictionary for request headers.
    local_version_info = read_local_version()  # Read the locally stored version information.
    if local_version_info and 'Etag' in local_version_info:
        headers['If-None-Match'] = local_version_info['Etag']  # If an ETag is available locally, add it to the headers for conditional request.

    response = session.get(GITHUB_API_URL, headers=headers)  # Make a GET request to the GitHub API.

    if response.status_code == 304:  # Not Modified
        return None  # If the server returns 304, it means there's no new release.

    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx).
    latest_release = response.json()  # Parse the JSON response from the GitHub API.
    return latest_release, response.headers.get('Etag')  # Return the release data and the ETag from the response headers.


def read_local_version() -> Optional[Dict[str, str]]:
    """Reads the local version information from the version file."""
    if os.path.exists(LOCAL_VERSION_FILE):  # Check if the local version file exists.
        with open(LOCAL_VERSION_FILE, "r") as f:  # Open the file in read mode.
            lines = f.read().splitlines(False)  # Read the lines from the file, discarding trailing newline characters.
            if len(lines) >= 3:  # Check if the file contains at least 3 lines (version, last_modified, last_check).
                return {
                    'version': lines[0],  # The first line is the version.
                    'last_modified': lines[1],  # The second line is the last modified date/time.
                    'last_check': lines[2]  # The third line is the last check date/time.
                }
    return None  # Return None if the file doesn't exist or doesn't have the expected content.


def save_local_version(version: str, last_modified: str) -> None:
    """Saves the latest version information to the local version file."""
    now = datetime.now(timezone.utc).isoformat()  # Get the current UTC time in ISO format.
    with open(LOCAL_VERSION_FILE, "w") as f:  # Open the file in write mode, overwriting existing content.
        f.write(f"{version}\n{last_modified}\n{now}")  # Write the new version, last modified date, and current time to the file.


def download_file(session: requests.Session, url: str, dest_path: str) -> None:
    """Downloads a file from the given URL to the specified destination path."""
    response = session.get(url)  # Make a GET request to the file URL.
    response.raise_for_status()  # Raise an exception for bad status codes.
    with open(dest_path, "wb") as f:  # Open the destination file in binary write mode.
        f.write(response.content)  # Write the content of the response to the file.


def should_check_update() -> bool:
    """Determines if an update check should be performed based on the last check time."""
    local_version_info = read_local_version()  # Read the local version information.
    if not local_version_info or 'last_check' not in local_version_info:
        return True  # If no local version info or last check time is available, perform a check.
    last_check = datetime.fromisoformat(local_version_info['last_check'])  # Parse the last check time from the local info.
    return datetime.now(timezone.utc) - last_check > CHECK_INTERVAL  # Return True if the time since the last check exceeds the defined interval.


def update_lib() -> None:
    """Checks for updates and downloads the latest version of the dependency if available."""
    if not should_check_update():
        return  # If it's not time to check for an update, exit the function.

    session = requests.Session()  # Create a new requests session.

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)  # Ensure the download directory exists.

    result = get_latest_release(session)  # Fetch the latest release information from GitHub.
    if result is None:
        return  # If no new release is available, exit the function.

    latest_release, last_modified = result  # Unpack the result.
    latest_version = latest_release["tag_name"]  # Extract the tag name as the latest version.
    local_version_info = read_local_version()  # Read the local version information.

    if local_version_info and latest_version == local_version_info['version']:
        return  # If the latest version is the same as the local version, no update is needed.

    print(f"New version found: {latest_version}. Updating...")  # Notify the user about the new version.

    assets = latest_release["assets"]  # Get the list of assets for the latest release.
    dependency = CURRENT_DEPENDENCY_FILENAME.rsplit(".", 1)[0]  # Extract the base name of the dependency file.
    for asset in assets:  # Iterate through the assets.
        if asset["name"].startswith(dependency):  # Check if the asset name starts with the dependency base name.
            download_url = asset["browser_download_url"]  # Get the download URL of the asset.
            dest_path = os.path.join(DOWNLOAD_DIR, CURRENT_DEPENDENCY_FILENAME)  # Construct the destination path for the downloaded file.
            download_file(session, download_url, dest_path)  # Download the file.
            print(f"Downloaded {CURRENT_DEPENDENCY_FILENAME} from {download_url}")  # Notify the user about the download.
            break  # Exit the loop after downloading the correct asset.
    else:
        print(f"Could not find asset for {CURRENT_DEPENDENCY_FILENAME}")  # Notify the user if the correct asset was not found.
        return

    save_local_version(latest_version, last_modified)  # Save the new version information locally.
    print(f"Updated to version {latest_version}")  # Notify the user about the successful update.


if __name__ == "__main__":
    update_lib()  # If the script is run directly, execute the update function.