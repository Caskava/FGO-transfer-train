import discord
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
import asyncio
import os

# Set up logging
logging.basicConfig(level=logging.INFO)

# Suppress googleapiclient.discovery_cache warnings
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

# Google Docs API setup
SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]
SERVICE_ACCOUNT_FILE = "fgo-448323-298faf2001f2.json"  # Update this path
DOCUMENT_ID = "1-DC0VS3Pz_Y5BW5xltLwh44nF0_6aQUNwme-0CVIrDU"  # Replace with your document ID

# Load Google Docs API credentials
try:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
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
            description="```diff\n- USED TRANSFER CODE\n```\n"
                       "# DO NOT ATTEMPT TO RE-ENTER",
            color=11804190,  # USED embed color
        )
    elif status == "UNUSED":
        # UNUSED Embed
        embed = discord.Embed(
            description='```json\n"UNUSED TRANSFER CODE"\n```\n'
                       "# DO NOT ATTEMPT TO RE-ENTER",
            color=2012298,  # UNUSED embed color
        )
    else:
        # Default Embed (fallback for invalid status)
        embed = discord.Embed(
            description="```diff\n- INVALID STATUS\n```\n"
                       "# DO NOT ATTEMPT TO RE-ENTER",
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

# Run the bot
try:
    client.run(os.getenv("DISCORD_BOT_TOKEN"))  # Read token from environment variable
except Exception as e:
    logging.error(f"Failed to start the bot: {e}")
