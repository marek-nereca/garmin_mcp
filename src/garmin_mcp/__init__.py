"""
Modular MCP Server for Garmin Connect Data
"""

import os
import sys
from pathlib import Path

import requests
from garminconnect import Garmin, GarminConnectAuthenticationError
from garth.exc import GarthHTTPError
from mcp.server.fastmcp import FastMCP
from tomllib import load as load_toml

from garmin_mcp import (
    activity_management,
    challenges,
    data_management,
    devices,
    gear_management,
    health_wellness,
    training,
    user_profile,
    weight_management,
    womens_health,
    workouts,
)


def _get_version() -> str:
    """Get version from pyproject.toml."""
    # Find project root (parent of src directory)
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    pyproject_path = project_root / "pyproject.toml"

    try:
        with open(pyproject_path, "rb") as f:
            pyproject = load_toml(f)
            return pyproject["project"]["version"]
    except (FileNotFoundError, KeyError):
        # Fallback version if pyproject.toml cannot be read
        return "0.0.0"


__version__ = _get_version()

# Import all modules


def get_mfa() -> str:
    """Get MFA code from user input"""
    print("\nGarmin Connect MFA required. Please check your email/phone for the code.")
    return input("Enter MFA code: ")


# Get credentials from environment
email = os.environ.get("GARMIN_EMAIL")
password = os.environ.get("GARMIN_PASSWORD")
tokenstore = os.getenv("GARMINTOKENS") or "~/.garminconnect"
tokenstore_base64 = os.getenv(
    "GARMINTOKENS_BASE64") or "~/.garminconnect_base64"

# Get MCP server mode from environment
mcp_mode = os.getenv("MCP_MODE", "stdio").lower()


def init_api(email, password):
    """Initialize Garmin API with your credentials."""

    try:
        # Using Oauth1 and OAuth2 token files from directory
        print(
            f"Trying to login to Garmin Connect using token data from directory '{tokenstore}'...\n"
        )

        # Using Oauth1 and Oauth2 tokens from base64 encoded string
        # print(
        #     f"Trying to login to Garmin Connect using token data from file '{tokenstore_base64}'...\n"
        # )
        # dir_path = os.path.expanduser(tokenstore_base64)
        # with open(dir_path, "r") as token_file:
        #     tokenstore = token_file.read()

        garmin = Garmin()
        garmin.login(tokenstore)

    except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError):
        # Session is expired. You'll need to log in again
        print(
            "Login tokens not present, login with your Garmin Connect credentials to generate them.\n"
            f"They will be stored in '{tokenstore}' for future use.\n"
        )
        try:
            garmin = Garmin(
                email=email, password=password, is_cn=False, prompt_mfa=get_mfa
            )
            garmin.login()
            # Save Oauth1 and Oauth2 token files to directory for next login
            garmin.garth.dump(tokenstore)
            print(
                f"Oauth tokens stored in '{tokenstore}' directory for future use. (first method)\n"
            )
            # Encode Oauth1 and Oauth2 tokens to base64 string and safe to file for next login (alternative way)
            token_base64 = garmin.garth.dumps()
            dir_path = os.path.expanduser(tokenstore_base64)
            with open(dir_path, "w") as token_file:
                token_file.write(token_base64)
            print(
                f"Oauth tokens encoded as base64 string and saved to '{dir_path}' file for future use. (second method)\n"
            )
        except (
            FileNotFoundError,
            GarthHTTPError,
            GarminConnectAuthenticationError,
            requests.exceptions.HTTPError,
        ) as err:
            print(err)
            return None

    return garmin


def main():
    """Initialize the MCP server and register all tools"""

    # Initialize Garmin client
    garmin_client = init_api(email, password)
    if not garmin_client:
        print("Failed to initialize Garmin Connect client. Exiting.")
        return

    print("Garmin Connect client initialized successfully.")

    # Configure all modules with the Garmin client
    activity_management.configure(garmin_client)
    health_wellness.configure(garmin_client)
    user_profile.configure(garmin_client)
    devices.configure(garmin_client)
    gear_management.configure(garmin_client)
    weight_management.configure(garmin_client)
    challenges.configure(garmin_client)
    training.configure(garmin_client)
    workouts.configure(garmin_client)
    data_management.configure(garmin_client)
    womens_health.configure(garmin_client)

    # Create the MCP app
    app = FastMCP(f"Garmin Connect v{__version__}")

    # Register tools from all modules
    app = activity_management.register_tools(app)
    app = health_wellness.register_tools(app)
    app = user_profile.register_tools(app)
    app = devices.register_tools(app)
    app = gear_management.register_tools(app)
    app = weight_management.register_tools(app)
    app = challenges.register_tools(app)
    app = training.register_tools(app)
    app = workouts.register_tools(app)
    app = data_management.register_tools(app)
    app = womens_health.register_tools(app)

    # Add activity listing tool directly to the app
    @app.tool()
    async def list_activities(limit: int = 5) -> str:
        """List recent Garmin activities"""
        try:
            activities = garmin_client.get_activities(0, limit)

            if not activities:
                return "No activities found."

            result = f"Last {len(activities)} activities:\n\n"
            for idx, activity in enumerate(activities, 1):
                result += f"--- Activity {idx} ---\n"
                result += f"Activity: {activity.get('activityName', 'Unknown')}\n"
                result += (
                    f"Type: {activity.get('activityType', {}).get('typeKey', 'Unknown')}\n"
                )
                result += f"Date: {activity.get('startTimeLocal', 'Unknown')}\n"
                result += f"ID: {activity.get('activityId', 'Unknown')}\n\n"

            return result
        except Exception as e:
            return f"Error retrieving activities: {str(e)}"

    # Run the MCP server based on the configured mode
    print(f"Starting MCP server in {mcp_mode} mode...")

    if mcp_mode == "stdio":
        # Default stdio mode
        app.run()
    elif mcp_mode == "sse":
        # Server-Sent Events mode
        print("Starting SSE server...")
        app.run(transport="sse")
    elif mcp_mode == "http":
        # Server-Sent Events mode
        print("Starting SSE server...")
        app.run(transport="streamable-http")
    else:
        print(
            f"ERROR: Unknown MCP_MODE '{mcp_mode}'. Supported modes: stdio, sse")
        sys.exit(1)


if __name__ == "__main__":
    main()
