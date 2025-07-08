import datetime
import os.path
from typing import Optional

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from loguru import logger
from pydantic import BaseModel, Field

# --- IMPORTANT ---
# To create events, the scope must be changed from .readonly to the full access scope.
# If you change the scope, you MUST delete the existing 'token.json' file to re-authenticate.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


class ListEventsArgs(BaseModel):
    """Input model for listing calendar events."""

    max_results: int = Field(
        10, description="Maximum number of events to return.", gt=0, le=50
    )


class CreateEventArgs(BaseModel):
    """Input model for creating a new calendar event."""

    summary: str = Field(..., description="The title or summary of the event.")
    start_time: str = Field(
        ...,
        description="The start time of the event in ISO 8601 format (e.g., '2025-07-07T10:00:00-04:00').",
    )
    end_time: str = Field(
        ...,
        description="The end time of the event in ISO 8601 format (e.g., '2025-07-07T11:00:00-04:00').",
    )
    description: Optional[str] = Field(
        None, description="An optional description or notes for the event."
    )


def _get_calendar_service():
    """Authenticates and returns a Google Calendar service object."""
    creds = None
    token_path = "token.json"
    creds_path = "credentials.json"

    if not os.path.exists(creds_path):
        raise FileNotFoundError(
            f"Error: Google Calendar API credentials not found at '{creds_path}'. "
            "Please download them from the Google Cloud Console and place them in the project root."
        )

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                logger.info("Refreshing expired Google API token.")
                creds.refresh(Request())
            except RefreshError as e:
                logger.error(f"Token refresh failed: {e}. Please re-authenticate.")
                os.remove(token_path)  # Remove bad token
                creds = None  # Force re-authentication
        if not creds:
            logger.info("Performing new Google API authentication.")
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token:
            token.write(creds.to_json())
            logger.success(f"Google API token saved to {token_path}")

    return build("calendar", "v3", credentials=creds)


def list_upcoming_events(args: ListEventsArgs) -> str:
    """Lists upcoming events from the user's primary Google Calendar."""
    try:
        service = _get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + "Z"

        logger.info(f"Fetching next {args.max_results} calendar events.")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=args.max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        if not events:
            return "No upcoming events found."

        event_list = [
            f"- {e['start'].get('dateTime', e['start'].get('date'))}: {e['summary']}"
            for e in events
        ]
        return "Upcoming events:\n" + "\n".join(event_list)
    except HttpError as e:
        logger.error(f"Google API HTTP error: {e}")
        return f"Error communicating with Google Calendar API: {e}"
    except Exception as e:
        logger.opt(exception=True).error(
            f"An unexpected error occurred in list_upcoming_events: {e}"
        )
        return f"An unexpected error occurred: {e}"


def create_calendar_event(args: CreateEventArgs) -> str:
    """Creates a new event in the user's primary Google Calendar."""
    try:
        service = _get_calendar_service()
        event = {
            "summary": args.summary,
            "description": args.description,
            "start": {
                "dateTime": args.start_time,
                "timeZone": "America/New_York",
            },  # Example timezone
            "end": {"dateTime": args.end_time, "timeZone": "America/New_York"},
        }

        logger.info(f"Creating calendar event: '{args.summary}'")
        created_event = (
            service.events().insert(calendarId="primary", body=event).execute()
        )

        url = created_event.get("htmlLink")
        logger.success(f"Event created successfully. URL: {url}")
        return f"Event '{created_event['summary']}' created successfully. View it here: {url}"
    except HttpError as e:
        logger.error(f"Google API HTTP error while creating event: {e}")
        return f"Error creating event via Google Calendar API: {e}"
    except Exception as e:
        logger.opt(exception=True).error(
            f"An unexpected error occurred in create_calendar_event: {e}"
        )
        return f"An unexpected error occurred: {e}"
