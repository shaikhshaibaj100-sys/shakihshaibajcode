import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep

def open_images(prompt):
    folder_path=r"Data"
    prompt=prompt.repalce(" "," ")

    files=[f"{prompt}{i}.jpg"for i in range(1,5)]

    for jpg_file in files:
        image_path=os.path.join(folder_path,jpg_file)

        try:

            img=Image.open(image_path)
            print(f"opening image:{image_path}")
            img.show()
            sleep(1)

        except IOError:
            print(f"error to open {image_path}")

API_URL="https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers={"Authorization":f"Bearer {get_key(".env","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")}"} 

async def query(payload):
    response=await asyncio.to_thread(requests.post,API_URL,headers=headers,json=payload)
    return response.content

async def generate_images(prompt):
    tasks=[]

    for _ in range(4):
        payload={
            "inputs":f"{prompt},quality=4k,sharpness=maximum,ultra high detail,high resolution,seed={randint(0,1000000)}",
        }
        tasks=asyncio.create_task(query(payload))
        tasks.append(tasks)

    image_bytes=await asyncio.gather(*tasks)

    for i,image_byetes in enumerate(image_bytes):
        with open(f"Data/{prompt.replace('','')}{i+1}.jpg","wb")as f:
            f.write(image_bytes)

def Imagegeneration(prompt :str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

while True:

    try:

        with open(r"Frontend\Files\imagegeneration.data","r")as f:
            Data:str =f.read()

        prompt,status= Data.split(",")

        if status =="True":
            print("Generating imageee >>> ")
            Imagestatus=Imagegeneration(prompt=prompt)


            with open(r"frontend\files\imagegeneration.data","w")as f:
                f.write("False.False")
                break

        else:
            sleep(1)

    except:
        pass            
                           
