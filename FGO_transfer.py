import discord
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO)

# Suppress googleapiclient.discovery_cache warnings
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

# Google Docs API setup
SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]

# Read Google service account credentials from environment variable
credentials_json = os.getenv({
  "type": "service_account",
  "project_id": "fgo-448323",
  "private_key_id": "721405b9558689496bad9e8a0e9a06bdc1d5e1f5",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC6uLiXFVW8Lbpd\nPvUbwZ/CFGCROypNFR1R76qQJJ5fa4LbBuokr2eWgdKjRJECVy3aT4/VBqjbUnjW\nDILCOZbqhFWOcZm9g5vw41U7ytOvjsfY96sVnhpRsr+vfZ6EKbOqsEGLGkDYKDTE\nnQNQ1lxuCiEKwe7UUkCptvouorunN49U7B2MMrpSNt5Sj25j7J6TVaGyAmWk3ReD\nvNbgKtITtImudYc9SjLGyylT3o5gxhe7YSnPjg/quuJR3jHOnIo/6YHbFHzOPBO8\nG6zYlQJzUa7rz29U8bh6fRGS5dXzDXsKKwFhoayrZgICzIWlnOrHPSm/rdRR5ojM\nv7gtZe0VAgMBAAECggEAO0aK6wON3RhTMmjbHP2hvtYDNfenXSMX1LwV1H6bfEVA\nHFIcoJrCcsgx2zzYH/sXBlf9nC3qCv4qeCEunYP0wexS0M6FdOFD7vvsQfgIrZHR\nJbKyMEGpr0fkjEx/twsaC1S66fLipPxWjBggRlhWrWQvyx93txWJi5cX4xgsJE/1\n4FqLeiLQIlXYdE9PsWGfGH6y6jn7Z1tZNqLo3S8mGDii387+cPP8DDs+4RZ6l01g\n4H3BAjc+VI21LQyqoCl/g7hjDgVEe2NLdhCyFC6AuOWX0MopHLwrLQxWdi/JwxDz\nIG8jbLRxPudLOR+gH3A6n3Wl9L8LJdH8zvRgsxDivQKBgQD6+SW9c6KMI9PC9A01\nigxlydspM0P7fgqGrtT5HQ6Cy7OVBq8HhnxdtkzAvPxiIJUdXacgA4PjzFKwlVls\npmF43bq4bh7fpTkCfbXCCwS0UjnxjhAMd7PZMBLAFQt4LVo1zfxXqY0ABatDUYyL\nVkEGXX0ANCxGeJ8eF4H7FDUK5wKBgQC+diBf0R5L+BlRaN9FO8GTwSaPRaau8Xjk\n5dXlKx9SJ/DfSfQSkl1OM66Eyakk9OxzYoFn3foYe6CQyyBUoekln0PBwTfhirbd\nsd0i0M4TfgbJjjQ1YyBEpGGWhusjZoCJIL1NGm8jsQGbNnNVryWgqsP4vVDN1cU8\nwCDptbykowKBgQCcUdsD6aZxC0+2ujQQCPA35kavntLVLmh4AyV8FHEZXq94PzV9\nxnJoHEgqNIwuwoSeSdrywb3AgV9vxVZxqiBEHDdU8KIiQtMDjjFLr3k6p4yXvBia\n62QF/z9ujK0cKYNqx+ZI476DKQTHZV/Y2dyejlRxcA2zxyW0pIe9T5TKOQKBgCuZ\n6UFmIxRrIIilhG9aBa+oiQZFgKoN94oXH4dN/uaU5CyJxok13oxXgn09mS4vr62e\ngFdh1q4iJxjel3Eoe7I0KpPBguRsF/7ah/A/ct29fRpJJqSOI8XzB7ApBM1e2tAJ\noaxz/7tg+ygoJ/EWnnuQfDqGRGhKptOIfEBkbWIXAoGBAKh+PQRz5AB/fdtiZLr3\nH0Rjs1HBSFa/KzJawGX5O6WJfs3jBtnEbDtoO/UV75N6Y77GaV4pac9INW8L2Bif\n3+tfU/rtdiPjH+qQXNgpbfSonbfWiOttkFqL5jIlWPBpT2B2C+GcyRbcQgsiQrMo\nuZBAPYRoZe/N6cx4e18IOB/v\n-----END PRIVATE KEY-----\n",
  "client_email": "transfer-codes@fgo-448323.iam.gserviceaccount.com",
  "client_id": "117554026993381649225",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/transfer-codes%40fgo-448323.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
")
if not credentials_json:
    logging.error("GOOGLE_CREDENTIALS environment variable is missing.")
    exit(1)

# Parse the JSON credentials
try:
    credentials_info = json.loads(credentials_json)
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info, scopes=SCOPES
    )
    service = build("docs", "v1", credentials=credentials)
except Exception as e:
    logging.error(f"Failed to initialize Google Docs API: {e}")
    exit(1)

# Function to read Google Docs document
def read_google_doc():
    try:
        doc = service.documents().get(documentId=DOCUMENT_ID).execute()
        content = doc.get("body", {}).get("content", [])
        text = ""

        for element in content:
            if "paragraph" in element:
                for paragraph_element in element["paragraph"]["elements"]:
                    if "textRun" in paragraph_element:
                        text += paragraph_element["textRun"].get("content", "")

        return text
    except HttpError as e:
        logging.error(f"Google Docs API error: {e}")
        return None

# Function to create an embed
def create_embed(transfer_number, password, status):
    # Normalize the status to uppercase
    status = status.upper() if status else None

    if status == "USED":
        # USED Embed
        embed = discord.Embed(
            description=f"```diff\n- USED TRANSFER CODE\n```\n"
                       f"# DO NOT ATTEMPT TO RE-ENTER",
            color=11804190,  # USED embed color
        )
    elif status == "UNUSED":
        # UNUSED Embed
        embed = discord.Embed(
            description=f'```json\n"UNUSED TRANSFER CODE"\n```\n'
                       f"# DO NOT ATTEMPT TO RE-ENTER",
            color=2012298,  # UNUSED embed color
        )
    else:
        # Default Embed (fallback for invalid status)
        embed = discord.Embed(
            description="```diff\n- INVALID STATUS\n```\n"
                       f"# DO NOT ATTEMPT TO RE-ENTER",
            color=0xFF0000,  # Red color for errors
        )

    # Add transfer number and password to the embed title
    embed.title = f"Transfer number: ||{transfer_number}||\nPassword: ||{password}||"

    # Set the thumbnail (top-right small image)
    embed.set_thumbnail(url="https://avatarfiles.alphacoders.com/327/thumb-1920-327656.png")

    # Set the body image (main image)
    embed.set_image(url="https://cdn.discordapp.com/attachments/1330706658573156444/1330751271808012318/q5qv2difk4i91.jpg?ex=678f1e33&is=678dccb3&hm=2f589df7e343b189592c8567477fa346cb47ee9079de2ad0be68a3c744c4d98a")

    return embed

# Discord bot setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user}")
    channel = client.get_channel(1330657589461123155)  # Replace with your channel ID
    last_status = None

    while True:
        # Read the Google Docs document
        text = read_google_doc()
        if text:
            logging.info("Google Docs content read successfully.")
            # Parse the document
            lines = text.splitlines()
            transfer_number = None
            password = None
            status = None

            for line in lines:
                if "Transfer number:" in line:
                    transfer_number = line.split("Transfer number:")[1].strip()
                elif "Password:" in line:
                    password = line.split("Password:")[1].strip()
                elif "Status:" in line:
                    status = line.split("Status:")[1].strip()
                elif "—" in line:  # Handle em dash or en dash
                    status = line.split("—")[1].strip()
                elif "-" in line:  # Handle standard hyphen
                    status = line.split("-")[1].strip()

            # Log the parsed values for debugging
            logging.info(f"Parsed values - Transfer number: {transfer_number}, Password: {password}, Status: {status}")

            # Validate the transfer number and password
            if transfer_number and password == "Samir2009":
                logging.info(f"Transfer number: {transfer_number}, Password: {password}, Status: {status}")
                if status != last_status:
                    # Create the embed
                    embed = create_embed(transfer_number, password, status)
                    logging.info("Embed created successfully.")

                    # Validate the embed before sending
                    if embed is not None:  # Ensure the embed is not None
                        # Send a new embed message
                        await channel.send(embed=embed)
                        logging.info("Embed sent to the channel.")
                    else:
                        logging.warning("Embed is None. Skipping send.")

                    last_status = status
            else:
                logging.warning("Invalid transfer number or password.")
        else:
            logging.warning("Failed to read Google Docs document.")

        await asyncio.sleep(5)  # Check every 5 seconds

# Read the Discord bot token from environment variable
DISCORD_BOT_TOKEN = os.getenv("MTMzMDY4ODk3Njc5NjkxMzc3Ng.GVP0k9.K5IWuY0JoBacd_IxuY0vc2cY2LYBl5Xborlw3s
")
if not DISCORD_BOT_TOKEN:
    logging.error("DISCORD_BOT_TOKEN environment variable is missing.")
    exit(1)

# Run the bot
try:
    client.run(DISCORD_BOT_TOKEN)
except Exception as e:
    logging.error(f"Failed to start the bot: {e}")
