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

# Hugging Face API configuration
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {
    "Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"
}

# Async function to send request to Hugging Face
async def query(payload):
    response = await asyncio.to_thread(
        requests.post, API_URL, headers=headers, json=payload
    )
    return response.content

# Async function to generate 4 images based on prompt
async def generate_images(prompt: str):
    tasks = []

    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}"
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        with open(fr"Data\{prompt.replace(' ', '_')}{i + 1}.jpg", "wb") as f:
            f.write(image_bytes)

# Wrapper to handle full image generation process
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# Monitor file and generate images on request
while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            data: str = f.read()
            prompt, status = data.split(",")

            if status == "True":
                print("Generating Images...")
                imgstatus = GenerateImages(prompt=prompt)

                with open(r"Frontend\Files\ImageGeneration.data","w") as f:
                    f.write("False, False")
                    break
            else:
                sleep(1)
    except:
        pass
