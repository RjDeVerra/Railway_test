from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import speech_recognition as sr
from moviepy.editor import *
from pydub import AudioSegment
import os
import sqlalchemy as db

API_TOKEN = ''

engine = db.create_engine("sqlite:///products-sqlalchemy.db")
connection = engine.connect()
metadata = db.MetaData()

products = db.Table("messages", metadata,
	db.Column("id", db.Integer, primary_key=True),
	db.Column("message", db.Text)
	)

metadata.create_all(engine)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

AudioSegment.converter = os.getcwd() + '\\ffmpeg.exe'
AudioSegment.ffprobe =  os.getcwd() + '\\ffprobe.exe'

r = sr.Recognizer()

ikb = InlineKeyboardMarkup(row_width=2)
ib1 = InlineKeyboardButton(text="Как это сделать", url="https://www.youtube.com/shorts/sQW9WqZJzqM")

ikb.add(ib1)

@dp.message_handler(commands=['start'])
async def send_message(message: types.Message):
   await message.answer(text="Как прислать кружок боту?", reply_markup=ikb)

@dp.message_handler(content_types=["video_note"])
async def send_video(message: types.Message):
	file_id = message.video_note.file_id
	file = await bot.get_file(file_id)
	await bot.download_file(file.file_path, "video_note.mp4")
	video = VideoFileClip("video_note.mp4")
	video.audio.write_audiofile("example.mp3")
	sound = AudioSegment.from_mp3(os.getcwd() + "\\example.mp3")
	sound.export("example.wav", format="wav")
	audio_file = sr.AudioFile('example.wav')
	with audio_file as source:
		audio = r.record(audio_file)
		text = r.recognize_google(audio, language = 'ru-RU', show_all = True)
		if text == []:
			await message.answer(text="Вы ничего не сказали, повторите попытку!", reply_markup=ikb)
		else:
			await message.answer(text=text['alternative'][0]['transcript'], reply_markup=ikb)
			i = products.insert().values({"message": text['alternative'][0]['transcript']})
			connection.execute(i)

if __name__ == '__main__':
   executor.start_polling(dp, skip_updates=True)