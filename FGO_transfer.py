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
credentials_json = os.getenv("{
  "type": "service_account",
  "project_id": "fgo-448323",
  "private_key_id": "298faf2001f21988c0d7e3e92e85e08d44fb94d0",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQC3HlGwR6JZapnv\nZW2t4wj72ZHNpAHrOZCdUpyl+SV01QIQOfVQH0cHhXYUpL+FJFWK7yF3wUtNLGN7\nnvGrHJF6LOI8xOVSmDrUyZClx63rMgPULD5Xd0HNpAVwysuG5E3jIe6SlFTmBtiM\nbfMsnT+2gSXdh8h/m72Q1t3+f8Y2WueCPp/TSZmYKMDIc3fa+mcBRQwPT9DH+a/N\nMeoyzX4gz+X6Qh1mIKaXpKn3HXALU+/uwXIDCJWwRnTViQ6XsparNaQCXzEfMD14\nglz3rERkVwKI1JvlLemvbmV4gsyd7AnHUw0mAYbEoudn/YlwbQJs01xR2EAmIec4\n3sudaI7ZAgMBAAECggEAAol9AEA905dSgqqZFmuq2DJvfrXjAOtPQZ6/ZN1K04+P\n88GZ0H5ecZA7zpVpweJ6/O3LPOmErZEL386X8pL2wQaWK9lehAJv7jrMsj9N/ZA3\n1Vy3kGaqlrrLCIEGyNuo6JizwXwkoPs/TNLJJ7kWBOVNLQCQmpQB0Fvpv3jtuhsK\nUS7BubxIlXva6DBSLS/840SHiwhl7uk3SnnzhF1XfwrmPEfdnYnfQ1YqFkUbrY/U\n/iYsl4zLqyxqC1JceCCFVBfXAgkinnxMqmlJXCW9L8tsd+X2ib7g9Chg1Sg6RFhI\nfIIBqIGC/Gd+o38PnVP+TCTPBlWQLK3c9a+rAVJ8sQKBgQDghgDjgFzTbqGSKztj\n8DVa82IrEwS1wqbJmYCyUAEAnQMz3Wj2vJiuPz7ZDsNfIg8MeI243cba5dQCAbpv\n8rkCf4zm5nAkFD91hlcYdQ8US9jbEwC9iJM04ApAvdsfmDSaFxk0HkgjoJ8XTvCw\nwXxQqMrx0G6gXUCj7INQnn3m0wKBgQDQylE3HDnvZAwllGoo60mJcdtR4l8h+2n2\nE8PT/Z9rXMfTDHehMQGKnMnI5BFXNPd7Jl3OFjRquqKZPtRRQXQX8dB2qNzSgajY\nGRcIVcIHEG0p6CxGMnpePqnI8r5kr0nPUwwgf4AD3oXGO4gFrwz+ahCLc7a7WKhp\nxNmYCcYAIwKBgQDYdXi/3I4hrSQJ9rIQXJIj+EcpffFphpsj+2DPCECfJcDjrM84\nKYUNYJ4nx4rl2cEmZcdEdlPzz+XAdYgXy6tAVFY0ee+daQPxOy4WvyxlheYw9zYc\nhGJfdKuN1Tw/To9QC3rZ+2PTLVSTtSBpWHCQltrpnOg6pQzfvPKws8xvzwKBgQC0\nDdVuBjx8ErZa7huCwC2BhxuRCPvrbUoauT7GoVCKoM9+VKER9BYVOFLXmL7PitDl\nddetcv6vD9ZK+6DTlfOM9q9EtSkBrGk0OqbfPD2AJA1P93W+76cRgU6gCZ5ha7zm\nOwMZP3rhW1PX+Ny7shMtj8BG0npCJBnQZL8VW1BSKwKBgQCNLc2lZF+XqAjjJAR6\n3W9CLpjUtprCEqSczJSg4SEPJngBG1qr6RDohnwd+nNhH3n2rcUoMW1B9rlgPhPW\nTyF0kRWf996iuchaWp/qEAGqOCZ2+w9MoETYo+i6bjw1uYtEZLad+ajOO7n3X+uy\nQDZuDAVKttrAOv0d5BD3hChOPA==\n-----END PRIVATE KEY-----\n",
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
