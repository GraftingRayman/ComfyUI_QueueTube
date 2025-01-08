import os
import time
from datetime import date

class GRQueueTube:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        string_type = ("STRING", {"multiline": True, "dynamicPrompts": True, "default": ","})
        int_type = ("INT", {"default": 1, "min": 1, "max": 99999})  # Max 5 digits
        return {"required": {
            "positive": string_type,
            "seed": int_type,
        }}

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("combined_prompts", "seed")
    FUNCTION = "queue_tube"
    CATEGORY = "GraftingRayman/YouTube"

    def queue_tube(self, positive, seed):
        # Construct the file path
        today = date.today().strftime("%Y-%m-%d")
        base_folder = r"H:\ComfyUI\custom_nodes\ComfyUI_GRTest\Chat"
        file_folder = os.path.join(base_folder, today)
        file_name = f"{seed:05d}_prompt.txt"  # Format seed with leading zeros
        file_path = os.path.join(file_folder, file_name)

        # Wait for the file to become available
        file_content = ""
        timeout = 30  # Maximum wait time: 5 minutes (300 seconds)
        interval = 10  # Check interval: 10 seconds
        elapsed_time = 0

        while not os.path.exists(file_path):
            if elapsed_time >= timeout:
                # Roll back the seed by 2
                updated_seed = seed - 2
                return (",a serene village atmosphere, with mountains in the background, the sun shining, some small farm houses and people walking alone a path", updated_seed)
            time.sleep(interval)
            elapsed_time += interval

        # If the file is found, read its content
        with open(file_path, "r", encoding="utf-8") as file:
            file_content = file.read()

        # Combine file content with the prompts
        combined_prompts = f"{file_content}\n{positive}"

        # Return the updated prompts and original seed
        return (combined_prompts, seed)
