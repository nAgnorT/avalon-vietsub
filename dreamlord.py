import os
import re
import sys
from asyncio import TimeoutError
from traceback import print_exc

import discord
from discord import DMChannel, Message
from discord.errors import Forbidden
from dotenv import load_dotenv

from avalon import avalon, confirm
from msgqueue import MsgQueue

load_dotenv()

client = discord.Client()
busyChannels = []
prefix = os.getenv("BOT_PREFIX", "+")
game_string = "The Resistance - Avalon. Type " + \
    prefix + "help or " + prefix + "avalon to begin."
game = discord.Game(name=game_string)
customprefix=''


@client.event
async def on_message(message):
    if message.author == client.user:			# we do not want the bot to reply to itself
        return

    # non-prefixed commands
    if len(message.mentions) == 1 and client.user in message.mentions and re.match(r"^<[@!]{1,2}[\d]+>$", message.content):
        await confirm(message)
        await message.channel.send('\nMy prefix is currently `' + prefix + '`')

    if not message.content.startswith(prefix):
        return

    command = message.content[len(prefix):]
    phase =''
    # change prefix
    #*if command.startswith('prefix'):
        #await confirm(message)
        #await message.channel.send('Hãy nhập prefix bạn mong muốn')
       # phase='Prefix'
       # with MsgQueue(client=client, check=message.channel) as msgqueue:
            #while phase=='Prefix':
                #reply=msgqueue.nextmsg()



    # prefixed commands
    if command.startswith('hello'):
        await confirm(message)
        msg = 'Chào {0.author.mention}'.format(message)
        await message.channel.send(msg)

    if command.startswith('avalon'):
        if message.channel in busyChannels:
            await message.channel.send("Một ván chơi đã bắt đầu ở kênh này rồi.")
        elif not isinstance(message.channel, DMChannel):
            await confirm(message)
            busyChannels.append(message.channel)
            await message.channel.send("Đang Khởi động **The Resistance: Avalon - Discord Edition** ở `#"+message.channel.name+"`...")
            await avalon(client, message, prefix)
            busyChannels.remove(message.channel)

    if command.startswith('help'):
        # message.channel.send()
        await confirm(message)
        await message.author.send('CÁCH CHƠI CƠ BẢN (luôn cập nhật): https://docs.google.com/document/d/17vx8lhQskBFa89KvhZnCBJgF6S2KGJvZWJAJ3Rvc8n0/edit?usp=sharing hoặc vào kênh Luật-chơi \n\nCÁC LỆNH CƠ BẢN:\n\n`' + prefix + 'avalon` - Bắt đầu trò chơi với chế độ thông thường\n`' + prefix + 'avalon sw` - Bắt đầu trò chơi với chế độ Star Wars\n`' + prefix + 'help` - Hướng dẫn.\n`' + prefix + 'stop` - Kết thúc ván chơi\n\nGửi lời cảm ơn đến tác giả gốc: https://github.com/ldeluigi')


@client.event
async def on_ready():
    print('Connected!')
    print('Username: ' + client.user.name)
    print('ID: ' + str(client.user.id))
    await client.change_presence(activity=game)


@client.event
async def on_error(event, *args, **kwargs):
    info = sys.exc_info()
    if info[0] == Forbidden and \
            event == "on_message" and \
            isinstance(args[0], Message):
        message = args[0]
        await message.channel.send(
            "```Error```\n:no_entry_sign: Không đủ quyền, tôi không thể làm điều đó. Gõ `" + prefix + "help` để được hướng dẫn."
        )
    elif info[0] == TimeoutError and \
            event == "on_message" and \
            isinstance(args[0], Message):
        message = args[0]
        await message.channel.send(
            "```Error```\n:alarm_clock: Đã xảy ra thời gian chờ. Trò chơi đã bị hủy. Bạn đã không hoạt động quá lâu."
        )
        busyChannels.remove(message.channel)
    else:
        print_exc()


def run(token):
    try:
        client.loop.run_until_complete(client.start(token))
    except KeyboardInterrupt:
        print('Bị gián đoạn - Đang tắt')
        client.loop.run_until_complete(client.change_presence(
            status=discord.Status.offline, activity=None))
    finally:
        client.loop.run_until_complete(client.close())


if __name__ == '__main__':
    run(os.getenv("SECRET_TOKEN"))
