"""
Discord wordle bot by Austiel
"""

import discord, random, os
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

token = '' # Your discord bot token
client = commands.Bot(command_prefix='$')

block_size = 22 # The size of letter block
font = ImageFont.truetype("arial.ttf", block_size - 10)
colors = {'g': (106, 170, 100), 'y': (201, 179, 88), 'b': (120, 124, 126)}

with open('words/words.txt','r') as fh1, open('words/allowed_words.txt','r') as fh2:
    word_list = fh1.read()
    allowed_words = fh2.read()

curr_word = random.choice(word_list.split()).upper()
tries = 0

def game_over(embed: discord.Embed, title:str, color:int, filename:str, desc = ''):
    global curr_word, tries
    embed.title = title
    embed.description = desc
    embed.color = color
    curr_word = random.choice(word_list.split())
    tries = 0
    os.remove(filename)

@client.command(aliases=['w'])
async def wordle(ctx):
    content = ctx.message.content.split()
    filename = 'temp.png'

    if len(content) > 1:
        answer = content[1].upper()
    else:
        await ctx.channel.send('Answer is missing')
        return

    if len(answer) != 5:
        await ctx.channel.send('Try a 5 letter word')
        return

    if not any((answer in word_list, answer in allowed_words)):
        await ctx.channel.send(f'{answer} is not in word list')
        return

    print(answer)
    try: # Fetch the recent image here. If none was found, it will raise an exception and create a new image instead
        recent_img = Image.open(filename)
        img_size = recent_img.size
        collage = Image.new("RGBA", (img_size[0], img_size[1] + block_size + 5), (41, 41, 41, 0))
        collage.paste(recent_img, (0, 0))
        recent_img.close()
    except FileNotFoundError:
        img_size = (0, 5)
        collage = Image.new("RGBA", (block_size * 5 + 20, block_size + 10), (41, 41, 41, 0))

    char_blocks = [] # a list of tuples each containing a character and its color. Ex. (char, 'g')
    char_count = {}
    for indx, char in enumerate(answer):
        if char not in curr_word:
            char_blocks.append((char, 'b'))
            continue

        if char == curr_word[indx]:
            count = char_count.get(char, 0)

            # If the character (char) has been counted as many times as its frequency in the word (curr_word),
            # this changes the color of the last yellow colored block of the same character into black.
            if count >= curr_word.count(char):
                i = char_blocks[::-1].index((char, 'y'))
                char_blocks[-i - 1] = (char, 'b')
            else: char_count[char] = count + 1

            char_blocks.append((char, 'g'))
        else:
            count = char_count.get(char, 0)
            if count < curr_word.count(char):
                char_count[char] = count + 1
                char_blocks.append((char, 'y'))
            else: char_blocks.append((char, 'b'))

    # Creates a character block then pastes it on the collage.
    for i, char_block in enumerate(char_blocks):
        img = Image.new('RGB', (block_size, block_size), colors[char_block[1]])
        d = ImageDraw.Draw(img)
        d.text((block_size/2, block_size/2), char_block[0], fill="white", anchor="mm", font=font)
        collage.paste(img, ((block_size + 5) * i, img_size[1]))

    collage.save(filename) # Saves in the same folder as the main bot file
    file = discord.File(filename)

    global tries
    tries += 1

    embed = discord.Embed()
    if answer == curr_word:
        print('Correct wordle')
        color = 0x6aaa64 # Green
        game_over(embed, 'Congratulations!', color, filename)

    if tries >= 6:
        print('Game over')
        color = 0xe74c3c # Red
        game_over(embed, curr_word, color, filename, 'Better luck next time.')

    embed.set_image(url=f"attachment://{filename}")
    await ctx.send(embed=embed, file = file)

client.run(token)
