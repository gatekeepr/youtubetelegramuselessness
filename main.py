from pytube import YouTube
from telegram.ext import Updater, CommandHandler
from telegram.error import TelegramError
from youtube_search import YoutubeSearch
import os
import re
import string
import sys

# initialising
token = open("config.txt", "r").read().strip()
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher
PATH = "./tmpdl/"


def downloadVideo(link):
    yt = YouTube(link)
    yt = (
        yt.streams.filter(progressive=True, file_extension="mp4")
        .order_by("resolution")
        .desc()
        .first()
    )
    if not os.path.exists(PATH):
        os.makedirs(PATH)
    pattern = re.compile("[\W_]+")
    filename = PATH + pattern.sub("", yt.title) + ".mp4"
    yt.download(PATH, filename=pattern.sub("", yt.title))
    filesize = int(os.path.getsize(filename) / (1024 * 1024))
    if filesize > 50:
        print(f"File {filename} too big with {filesize} MB.")
        os.remove(filename)
        return "errtoobig"
    else:
        print(f"File {filename} will be sent with {filesize} MB.")
        return filename


def createAnswer(keywords, isQuickplay):
    terms = " ".join([word for word in keywords])
    results = YoutubeSearch(terms, max_results=1).to_dict()
    for result in results:
        print(str(result) + "\n - - - ")
    name = results[0]["title"]
    link = "https://www.youtube.com" + results[0]["url_suffix"]
    answer = f"Here is {name}: \n{link}"
    print(answer)
    if isQuickplay:
        return link
    else:
        return answer


def quickplay(update, context):
    link = createAnswer(context.args, True)
    answer = downloadVideo(link)
    if answer == "errtoobig":
        context.bot.send_message(chat_id=update.message.chat_id, text="File too big!")
    else:
        try:
            context.bot.send_video(
                chat_id=update.message.chat_id,
                video=open(
                    answer,
                    "rb",
                ),
                supports_streaming=True,
            )
        except:
            print(f"Telegram failed to send!")
            context.bot.send_message(
                chat_id=update.message.chat_id, text="Something went wrong :-("
            )
        os.remove(answer)


def play(update, context):
    answer = createAnswer(context.args, False)
    context.bot.send_message(chat_id=update.message.chat_id, text=answer)


def dl(update, context):
    if len(context.args[0]) > 1:
        yt = YouTube(context.args[0])
        context.bot.send_message(
            chat_id=update.message.chat_id, text=f"Downloading: {yt.title}"
        )
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text="No link found!")
    answer = downloadVideo(context.args[0])
    if answer == "errtoobig":
        context.bot.send_message(chat_id=update.message.chat_id, text="File too big!")
    else:
        try:
            context.bot.send_video(
                chat_id=update.message.chat_id,
                video=open(answer, "rb"),
                supports_streaming=True,
            )
        except:
            print("Telegram failed to send!")
            context.bot.send_message(
                chat_id=update.message.chat_id, text="Something went wrong :-("
            )
        os.remove(answer)


# start polling
dispatcher.add_handler(CommandHandler("play", play))
dispatcher.add_handler(CommandHandler("dl", dl))
dispatcher.add_handler(CommandHandler("quickplay", quickplay))
updater.start_polling()
