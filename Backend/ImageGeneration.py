import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep


def open_images(prompt):
    folder_path = r"Data"
    prompt = prompt.replace(" ", "_")
    
    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]
    
    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)
        
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
            
        except IOError:
            print(f"Unable to open {image_path}")

# Using Pollinations AI which is free, fast, and requires no API keys
async def fetch_image(prompt: str, seed: int):
    # Format the prompt for the URL
    url_prompt = requests.utils.quote(f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution")
    url = f"https://image.pollinations.ai/prompt/{url_prompt}?seed={seed}&width=1024&height=1024&nologo=True"
    
    response = await asyncio.to_thread(requests.get, url)
    return response.content

async def generate_images(prompt: str):
    tasks = []

    for _ in range(1):
        seed = randint(0, 1000000)
        task = asyncio.create_task(fetch_image(prompt, seed))
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        with open(fr"Data\{prompt.replace(' ', '_')}{i + 1}.jpg", "wb") as f:
            f.write(image_bytes)

# Wrapper to handle full image generation process
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    # open_images(prompt) # Disabled to prevent opening windows on the server OS

# Monitor file and generate images on request
# NOTE: Wrapped in __main__ guard so this module can be safely imported
# by FastAPI (server.py) without blocking. The desktop app runs this
# as a subprocess (python Backend\ImageGeneration.py) so __main__ still fires.
if __name__ == "__main__":
    while True:
        try:
            with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
                data: str = f.read()
                prompt, status = data.split(",")

                if status == "True":
                    print("Generating Images...")
                    imgstatus = GenerateImages(prompt=prompt)

                    with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                        f.write("False, False")
                        break
                else:
                    sleep(1)
        except:
            pass
