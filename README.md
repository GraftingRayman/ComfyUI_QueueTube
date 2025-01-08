# ComfyUI QueueTube
These nodes allow your YouTube LiveStream viewers to create on your local ComfyUI, you can make this a members only feature with a screen behind you displaying your members creations

## Running
1: Start your YT LiveStream

2: Start YTChatListen.py

3: Use the GRPromptText Node

## Settings
1: Edit the following line in GRQueueTube.py and change the path to where the YTChatListen.py is saving the chat log, this is usually a folder in the ComfyUI custom_nodes directory

        base_folder = r"H:\ComfyUI\custom_nodes\ComfyUI_QueueTube\Chat"
        
2: Put your Google API client secret in a file called client_secrets.json


a file called nsfwwords.txt contains words that are blocked, this should prevent your channel from getting banned, but don't count on it, you need to monitor what users are typing and what is being accepted.

The chat/prompt logs are kept in a folder with the Date, Time, YT handle and the message it self


Users need to type "PROMPT:" and the prompt itself ie:


"PROMPT: A man on a boat fishing, wearing a blue cap and red jacket"

"PROMPT: A cat in a hat wearing a blue jersey"


That's it, enjoy prompting


