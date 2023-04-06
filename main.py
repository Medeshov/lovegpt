
import io
import os
import json
import openai
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InputFile
from elevenlabslib import *
import pydub

# Read configuration settings from file
with open('config.json', "r") as file:
    config = json.load(file)

openai.api_key = config['openai']
bot = Bot(config['token'])
dp = Dispatcher(bot)
user = ElevenLabsUser(config['eleven']) # Configure Eleven Labs API key





# Define a function to generate audio from text using Eleven Labs API
def generate_audio(text):
    voice = user.get_voices_by_name("Kai")[0]  # replace with your desired voice name
    audio_bytes = voice.generate_audio_bytes(text)
    return audio_bytes



messages= [
    {"role": "system","content": "You are assistant, be friendly and funny,bold, conversational"} 
    ]

def update(messages, role, content):
    messages.append({"role": role, "content": content})
    return messages

@dp.message_handler()


async def send(message: types.Message):
    update(messages, "user", message.text)
    response = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages= messages
    )
    audio_data = generate_audio(response['choices'][0]['message']['content']) # generate audio from OpenAI response
    audio = pydub.AudioSegment.from_file_using_temporary_files(io.BytesIO(audio_data)) # create audio segment
    audio_path = "/tmp/temp_audio.ogg"  # change this to a desired temporary file path
    audio.export(audio_path, format="mp3") # save audio as MP3
    with open(audio_path, "rb") as audio_file:   # send the audio file to the user
        await message.answer(response['choices'][0]['message']['content'])
        await bot.send_audio(message.chat.id, audio_file) 
    os.remove(audio_path) # delete the temporary audio file
    
    # await message.answer(response['choices'][0]['message']['content'])



dp.register_message_handler(send) # Register the message handler for incoming messages

executor.start_polling(dp, skip_updates=True)