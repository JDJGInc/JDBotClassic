from discord.ext import commands
import discord, random, typing, bisect
from difflib import SequenceMatcher
import utils
from discord.ext.commands.cooldowns import BucketType

class Dice(commands.Cog):
  "Commands that rely a ton on random chance"
  def __init__(self, bot):
    self.bot = bot

  async def generate_embed(self, ctx, number):
    if number < 1:  
      return await ctx.send("NO")

    url_dict = {20 : "https://i.imgur.com/9dbBkqj.gif", 6:"https://i.imgur.com/6ul8ZGY.gif"}
    url = url_dict.get(number, "https://i.imgur.com/gaLM6AG.gif")

    embed = discord.Embed(title = f"Rolled a {random.randint(1,number)}", color = random.randint(0, 16777215), timestamp =(ctx.message.created_at))

    embed.set_footer(text = f"{ctx.author.id}")
    embed.set_thumbnail(url = "https://i.imgur.com/AivZBWP.png")
    embed.set_author(name = f"d{number} Rolled by {ctx.author}:",icon_url = ctx.author.display_avatar.url)
    embed.set_image(url = url)
    await ctx.send(embed = embed)

  @commands.command(brief="A command to roll random dnd dice.",aliases=["roll"])
  async def diceroll(self, ctx, * , number:typing.Optional[int]=None):

    number = number or 6
    
    await self.generate_embed(ctx, int(number))

  @commands.command(brief = "Gives random emojis(from guild and bot)", help = "Please use this wisely.", aliases = ["e_spin","emoji_spin"])
  async def emoji_spinner(self, ctx):
    
    emoji_choosen = random.choice(self.bot.emojis)

    if emoji_choosen.available is False: emoji_choosen = emoji_choosen.url

    emoji_choice = None

    if isinstance(ctx.channel, discord.Thread):
      if ctx.guild.emojis:
        emoji_choice = random.choice(ctx.guild.emojis)
        if emoji_choice.available is False: emoji_choice = emoji_choice.url
    
    if isinstance(ctx.channel, discord.TextChannel):
      if ctx.guild.emojis:
        emoji_choice = random.choice(ctx.guild.emojis)
        if emoji_choice.available is False: emoji_choice = emoji_choice.url

    await ctx.send(f"{emoji_choosen} \n{emoji_choice}")
  
  @commands.command(brief="gives a random kawaii emoji.",aliases=["ka"])
  async def kawaii_random(self, ctx):
    kawaii_emotes= self.bot.get_guild(773571474761973840)
    kawaii_emotes2 = self.bot.get_guild(806669712410411068)
    kawaii_emotes3 = self.bot.get_guild(692576207404793946)
    emoji_choosen = random.choice(kawaii_emotes.emojis+kawaii_emotes2.emojis+kawaii_emotes3.emojis)
    await ctx.send(emoji_choosen)

  @commands.command(brief="a magic 8ball command(uses rng)",aliases=["8ball"])
  async def _8ball(self, ctx, *, args = None):
    if args is None:
      await ctx.send("Please give us a value to work with.")
    if args:
      responses = ["As I see it, yes.","Ask again later.","Better not tell you now.","Cannot predict now.","Concentrate and ask again.","Don’t count on it.","It is certain.","It is decidedly so.","Most likely.","My reply is no.","My sources say no.","Outlook not so good.","Outlook good.","Reply hazy, try again.","Signs point to yes.","Very doubtful.","Without a doubt.","Yes.","Yes – definitely.","You may rely on it."]
      await ctx.send(f"{random.choice(responses)}")

  @commands.command(brief="gordon ramsay insults you(I don't own his likeness)",help="Please only use if you can handle insults :D (with some profanity)")
  async def insult2(self, ctx, *, args = None):
    ramsay_responses=["You are getting your kn*ckers in a twist! Calm down!", "WHAT ARE YOU? An idiot sandwich", "You fucking Donkey!", "How about a thank you, you miserable wee-bitch", "Hey, panini head, are you listening to me?", "For what we are about to eat, may the Lord make us truly not vomit", "Do you want a fucking medal?", "That fucking gremlin, everything you touch, you screw... there you go", "Your name is Elsa, isn't it? Because this shit is so fucking frozen", "This pork is so raw it's still singing Hakuna Matata", "Fuck off you bloody donut", "This crab is so raw it just offered me a krabby patty","The fucking bass is fucking RAW!","This chicken is so raw it's still asking why it crossed the road!","Hey excuse me madam, fuck me? How about fuck you.","Move It, Grandpa"]

    if args is None:
      await ctx.send(content=f"{ctx.author}, {random.choice(ramsay_responses)}")

    if args:
      await ctx.send(random.choice(ramsay_responses))

  @commands.command(brief="a command meant to flip coins",help="commands to flip coins, etc.", aliases = ["coinflip", "cf"])
  async def coin(self, ctx):
    value = random.choice([True, False]) 
    
    view = utils.CoinFlip(ctx)

    embed2 = discord.Embed(color = random.randint(0, 16777215))
    embed2.set_image(url = "https://i.imgur.com/O7FscBW.gif")

    view.message = await ctx.send(content = "Time to see if you can guess correctly!", embed = embed2, view = view)

    await view.wait()

    if view.value is None:
      return await view.message.edit("Looks it like it timed out.(may want to make an new game)")

    if view.value == "Heads" and value: win = True
    elif view.value == "Tails" and not value:  win = True
    elif view.value == "Heads" and not value: win = False
    elif view.value == "Tails" and value: win = False
    
    pic_name = "Heads" if (value) else "Tails"

    url_dic = {"Heads": "https://i.imgur.com/MzdU5Z7.png","Tails":"https://i.imgur.com/qTf1owU.png"}

    embed = discord.Embed(title="coin flip", color=random.randint(0, 16777215))
    embed.set_author(name = f"{ctx.author}", icon_url = ctx.author.display_avatar.url)

    embed.add_field(name = "The Coin Flipped:", value = f"{pic_name}")
    embed.add_field(name = "You guessed:", value = f"{view.value}")
    embed.set_image(url = url_dic[pic_name])

    if win: embed.add_field(name="Result: ", value = "You won")
    else: embed.add_field(name="Result: ", value = "You lost")
    
    await view.message.edit(content = "Here's the results:", embed = embed)

  @commands.command(brief="a command to find the nearest emoji")
  async def emote(self, ctx, *, args=None):
    if args is None:
      await ctx.send("Please specify an emote")
    if args:
      emoji=discord.utils.get(self.bot.emojis,name=args)
      emoji = emoji or sorted(self.bot.emojis, key=lambda x: SequenceMatcher(None, x.name, args).ratio())[-1]
      emoji = emoji or "We haven't found anything"

      if not emoji.available: emoji = emoji.url
      await ctx.send(emoji, reference = ctx.message.reference, mention_author = False)

  @commands.command(brief="takes smallest and largest numbers then does a random number between.")
  async def random_number(self , ctx , *numbers: typing.Union[int,str]):
    numbers=sorted(list(filter(lambda x: isinstance(x, int), numbers)))
    if len(numbers) < 2:
      await ctx.send("Not enough numbers")

    else:
      embed = discord.Embed(title=f"Random Number: {random.randint(numbers[0],numbers[-1])} ",color=random.randint(0, 16777215))
      embed.add_field(name="Lowest Number:",value=f"{numbers[0]}")
      embed.add_field(name="Highest Number:",value=f"{numbers[-1]}")
      await ctx.send(embed=embed)


  @commands.command(brief = "sees how compatitable something is(two things)")
  async def works(self, ctx, *args : commands.clean_content):

    if len(args) < 2:
      return await ctx.send("you didn't give me enough objects to checks the status of two items and make sure to have two objects.")

    item1 = args[0]
    item2 = args[-1]

    item_relationship = random.randint(1, 100)

    responses = ["They don't work well together at ALL :angry:", "They work quite poorly together...", "They work kinda good together, maybe", "They work REALLY good together, wow. Nice.", "Let them collaborate anytime."]

    breakpoints = [51, 70, 89, 100, 101]
    i = bisect.bisect(breakpoints, item_relationship)
    resp = responses[i]

    embed = discord.Embed(title = f"How well does {item1} and {item2} work together?",  description = f"They work at a rate {item_relationship}% \n**{resp}**", color = random.randint(0, 16777215), timestamp = ctx.message.created_at)

    embed.set_author(name=f"{ctx.author}", icon_url = ctx.author.display_avatar.url)

    embed.set_footer(text = f"{ctx.author.id}")

    await ctx.send(embed = embed)

  @commands.cooldown(1, 15, BucketType.user)
  @commands.command(brief = "a nice rock scissors paper game with the bot")
  async def rps(self, ctx):
    view = utils.RpsGame(ctx)

    embed2 = discord.Embed(color = random.randint(0, 16777215))
    embed2.set_image(url = "https://i.imgur.com/bFYroWk.gif")

    view.message = await ctx.send("Rock Paper Scissors Shoot!", embed = embed2, view = view)

    await view.wait()

    if view.value is None:
      return await view.message.edit("You didn't respond fast enough, you lost.(Play again by running game again)")
    
    deciding = random.randint(1, 3)
    number_to_text = {1 : "Rock", 2 : "Paper", 3 : "Scissors"}

    embed = discord.Embed(title = "RPS Game",color = random.randint(0, 16777215), timestamp=ctx.message.created_at)

    if view.value == deciding:
      embed.set_author(name = "Tie!",icon_url = ctx.author.display_avatar.url)

    if view.value == 1 and deciding == 3 or view.value == 2 and deciding == 1 or view.value == 3 and deciding == 2:
      embed.set_author(name = "You Won!",icon_url = ctx.author.display_avatar.url)

    if view.value == 3 and deciding == 1 or view.value == 1 and deciding == 2 or view.value == 2 and deciding == 3:
      embed.set_author(name = "You lost!",icon_url = ctx.author.display_avatar.url)

    embed.set_footer(text = f"{ctx.author.id}")

    embed.add_field(name = "You Picked:", value = f"{number_to_text[view.value]}")
    embed.add_field(name = "Bot Picked:", value = f"{number_to_text[deciding]}")

    embed.set_image(url = "https://i.imgur.com/bFYroWk.gif")

    await view.message.edit(embed = embed, view = None)

    #gnome made a good idea on a run again button, I Just need to make one :D
    
def setup(bot):
  bot.add_cog(Dice(bot))