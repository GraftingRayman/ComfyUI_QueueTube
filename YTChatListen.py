from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import time
from datetime import datetime
import re


class YouTubeLiveChatOAuth:
    def __init__(self, client_secrets_file):
        """
        Initialize the class, authenticate, and load NSFW words.
        """
        self.client_secrets_file = client_secrets_file
        self.youtube = self.authenticate()
        self.nsfw_words = self.load_nsfw_words()

    def authenticate(self):
        """
        Authenticate using OAuth 2.0 and return an authorized YouTube API client.
        """
        SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
        flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, SCOPES)
        credentials = flow.run_local_server(port=8080, prompt="consent", authorization_prompt_message="")
        return build("youtube", "v3", credentials=credentials)

    def get_live_chat_id(self):
        """
        Retrieve the live chat ID for the currently active broadcast.
        """
        try:
            response = self.youtube.liveBroadcasts().list(
                part="snippet",
                broadcastStatus="active",
                broadcastType="all"
            ).execute()

            if "items" in response and len(response["items"]) > 0:
                live_chat_id = response["items"][0]["snippet"]["liveChatId"]
                return live_chat_id
            else:
                print("No active live broadcast found.")
                return None
        except Exception as e:
            print(f"Error retrieving live chat ID: {e}")
            return None

    def load_nsfw_words(self):
        """
        Load NSFW words from a file called 'nsfwwords.txt' in the same directory.
        """
        try:
            file_path = os.path.join(os.path.dirname(__file__), "nsfwwords.txt")
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            # Parse and return the words as a set for efficient filtering
            return set(word.strip().lower() for word in content.split(",") if word.strip())
        except FileNotFoundError:
            print("Error: 'nsfwwords.txt' not found. Ensure the file exists in the same directory.")
            return set()

    def contains_nsfw_words(self, message):
        """
        Check if the message contains any NSFW words.
        """
        # Tokenize the message into words
        message_words = re.findall(r'\b\w+\b', message.lower())
        return any(word in self.nsfw_words for word in message_words)

    def save_prompt_message(self, message):
        """
        Save messages starting with 'PROMPT:' in the Chat folder with a date-based structure,
        removing the 'PROMPT:' prefix before saving.
        """
        # Remove the "PROMPT:" prefix
        clean_message = re.sub(r"^PROMPT:? ?", "", message, flags=re.IGNORECASE).strip()

        # Define the base folder and current date folder
        base_folder = "Chat"
        current_date = datetime.now().strftime("%Y-%m-%d")
        date_folder = os.path.join(base_folder, current_date)

        # Ensure the folder structure exists
        os.makedirs(date_folder, exist_ok=True)

        # Determine the next file name
        existing_files = sorted(
            [f for f in os.listdir(date_folder) if f.endswith(".txt")],
            key=lambda x: int(x.split('_')[0]) if x.split('_')[0].isdigit() else 0
        )
        if existing_files:
            last_number = int(existing_files[-1].split('_')[0])
            next_number = last_number + 1
        else:
            next_number = 1

        file_name = f"{next_number:05d}_prompt.txt"
        file_path = os.path.join(date_folder, file_name)

        # Save the message to the file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(clean_message)
        print(f"Saved PROMPT message to: {file_path}")

    def log_message(self, username, message):
        """
        Log all messages with their username and timestamp to a log file.
        """
        log_folder = "log"
        current_date = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_folder, f"{current_date}.log")

        # Ensure the log folder exists
        os.makedirs(log_folder, exist_ok=True)

        # Append the log entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "a", encoding="utf-8") as file:
            file.write(f"[{timestamp}] {username}: {message}\n")

    def listen_to_chat(self, live_chat_id):
        """
        Listen to the live chat and print incoming messages, separating username and message.
        Save messages starting with 'PROMPT:' to the Chat folder, excluding those with NSFW words.
        Log all messages to a log file.
        """
        print("Listening to live chat...")
        next_page_token = None

        while True:
            try:
                response = self.youtube.liveChatMessages().list(
                    liveChatId=live_chat_id,
                    part="snippet,authorDetails",
                    pageToken=next_page_token,
                ).execute()

                # Display and process chat messages
                for item in response.get("items", []):
                    author_name = item["authorDetails"]["displayName"]
                    message = item["snippet"]["textMessageDetails"]["messageText"]

                    # Log the message
                    self.log_message(author_name, message)

                    # Print username and message
                    print(f"Username: {author_name}")
                    print(f"Message: {message}")
                    print("-" * 50)

                    # Check if the message contains NSFW words
                    if self.contains_nsfw_words(message):
                        print(f"Message contains NSFW content. Skipping: {message}")
                        continue

                    # Check if the message starts with variations of "PROMPT:"
                    if re.match(r"^PROMPT:? ?", message, flags=re.IGNORECASE):
                        self.save_prompt_message(message)

                # Get the token for the next page of comments
                next_page_token = response.get("nextPageToken", None)

                # Wait before the next poll to avoid exceeding the quota
                time.sleep(30)

            except Exception as e:
                print(f"Error while listening to chat: {e}")
                break


# Usage
if __name__ == "__main__":
    # Path to the client_secrets.json file
    CLIENT_SECRETS_FILE = "client_secrets.json"

    # Create YouTubeLiveChatOAuth instance
    yt_chat = YouTubeLiveChatOAuth(client_secrets_file=CLIENT_SECRETS_FILE)

    # Get the live chat ID
    live_chat_id = yt_chat.get_live_chat_id()
    if live_chat_id:
        # Listen to live chat
        yt_chat.listen_to_chat(live_chat_id)
