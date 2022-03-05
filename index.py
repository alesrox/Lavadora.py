import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure, MissingPermissions
from webserver import *
from math import log
from urls import *
from admin import *
from forex_python.converter import CurrencyCodes
import requests
import datetime
import asyncio
import json
import ast
import random
from airtable import * #upm package(airtable-python-wrapper)

version = ' 0.29.2'
c = CurrencyCodes()

marrytable = Airtable(base_key, 'Marry', api_key)

def bounded_eval(expression, bits = 9999):
    nums = expression.split('**')
    if len(nums) == 1:
        val = eval(expression)
        if log(val, 2) > bits:
            return "too large"
        else:
            return val
    else:
        base = nums[0]
        power = '**'.join(nums[1:])
        base = eval(base)
        power = eval(power)
        if power * log(base,2) > bits:
            return "too large"
        else:
            return pow(base, power)

def get_prefix(bot, ctx):
    try:
        with open('prefixes.json', 'r') as file:
            prefixes = json.load(file)
    
        return prefixes[str(ctx.guild.id)]
    except:
        return 'm!'

bot = commands.Bot(command_prefix=get_prefix, description='Bot creado por el Alex Ros', help_command=None)

@bot.event
async def on_message(ctx):
    if ctx.guild.id == 795073124688461936:
        if ctx.channel.id == 796369677525450813 and not ctx.content == 'm!verify':
            await ctx.delete()
        elif ctx.channel.id == 796369677525450813 and ctx.content == 'm!verify':
            role = discord.utils.get(ctx.guild.roles, name='New User')
            await ctx.author.remove_roles(role)
            await ctx.delete()

    await bot.process_commands(ctx)

@bot.event
async def on_member_join(member):
    server = member.guild.id
    if server == 795073124688461936:
        msg = 'Hola, bienvenido al servidor de Programación Code Time, porfavor para verificarte y que puedas acceder a todo lo demás del servidor ve al canal de roles y seguidamente al de verificación para poder verificarte, por favor y gracias.'
        await member.send(msg)

@bot.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        prefix = get_prefix(bot, general)
        await general.send(f'Hola, gracias por añadirme a {guild.name}!, si no sabeis mis comandos por favor {prefix}help')

@bot.event
async def on_guild_remove(guild):
    try:
        with open('prefixes.json', 'r') as file:
            prefixes = json.load(file)

        prefixes.pop(str(ctx.guild.id))

        with open('prefixes.json', 'w') as file:
            json.dump(prefixes, file, indent=4)
    except:
        pass

@bot.command()
@has_permissions(ban_members=True)
async def setprefix(ctx, prefix):
    with open('prefixes.json', 'r') as file:
        prefixes = json.load(file)

    prefixes[str(ctx.guild.id)] = str(prefix)

    with open('prefixes.json', 'w') as file:
        json.dump(prefixes, file, indent=4)
    
    await ctx.send(f'Prefix changed to: {prefix}')

@bot.command()
async def ping(ctx):
    embed = discord.Embed(title=f':ping_pong: | Pong! {round(bot.latency * 1000)}ms', color=discord.Color.blue())
    await ctx.send(embed=embed)

@bot.command()
async def status(ctx):
    embed = discord.Embed(title=f'{ctx.guild.name}', description='Lorem Ipsum', 
        timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.add_field(name='Server created at ', value=f'{ctx.guild.created_at}')
    embed.add_field(name='Server Owner ', value=f'{ctx.guild.owner}')
    embed.add_field(name='Server Region', value=f'{ctx.guild.region}')
    embed.add_field(name='Sever ID', value=f'{ctx.guild.id}')
    embed.set_thumbnail(url=f'{ctx.guild.icon_url}')
    await ctx.send(embed=embed)

@bot.command()
async def ownerinfo(ctx):
    AlexRos = bot.get_user(658254360056168468)
    embed = discord.Embed(title=f'Información de mi creador (AlexRos)', description='Otros proyectos de AlexRos',
        url=f'https://alexros.pythonanywhere.com/portfolio')
    embed.add_field(name='Discord Tag: ', value=f'{AlexRos}')
    embed.add_field(name='Instagram: ', value='aleex__ros')
    embed.add_field(name='GitHub: ', value='AlexRos10')
    embed.set_thumbnail(url=f'{AlexRos.avatar_url}')
    await ctx.send(embed=embed)

@bot.command()
async def botinfo(ctx):
    embed = discord.Embed(title=f'Lavadora Bot', description='Informacion del bot', 
        timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.add_field(name='Libreria usada: ', value=f'Discord.py (Python)')
    embed.add_field(name='Antigua Base de Datos: ', value=f'Un documento .txt')
    embed.add_field(name='Actual Base de Datos: ', value=f'Airtable y Un archivo .json')
    embed.add_field(name='Creador: ', value=f'AlexRos#7004')
    embed.add_field(name='Version:', value=f'{version}')
    embed.add_field(name='Prefix por defecto:', value=f'm!')
    embed.add_field(name='Prefix del server:', value=f'{get_prefix(bot, ctx)}')
    embed.set_footer(text=f'Lavadora is in {len(bot.guilds)} servers')
    embed.set_thumbnail(url=f'{bot.user.avatar_url}')
    await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    embed = discord.Embed(title=f'Help Command', description=f'Some commands can be added\nBot Version:{version}\nServer Prefix: {get_prefix(bot, ctx)}', 
        url='https://cdn.discordapp.com/avatars/658254360056168468/52952fea878cd24e0564f5c898948a44.webp', timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.add_field(name='Functions ', value=f'Status, Botinfo, Math,\nBitcoin [Current Coin], Convert [Binary] (Binary to Decimal), Avatar, Marry')
    embed.add_field(name='Actions [@User] ', value=f'Kiss, Hug, Kill, Pat, Marry, Marrystatus')
    embed.add_field(name='Actions ', value=f'Suicide, Cry, Smile, Sleep, Divorce')
    embed.add_field(name='Admin Functions ', value=f'setprefix [new prefix]')
    await ctx.send(embed=embed)

@bot.command()
async def math(ctx, *, math : str):
    try:
        if bounded_eval(math) == 'too large':
            await ctx.send('Lo siento mucho, pero por cuestiones de seguridad no podemos exponentar a un numero tan elevado que sobrepase una base de bits de 9999')
        else:
            await ctx.send(f'**{ctx.author.name}**, the answer is {eval(math)}')
    except:
        await ctx.send('Oh no, something went wrong')

@bot.command()
async def bitcoin(ctx, coin : str=None):
    try:
        if coin == None:
            await ctx.send(f'**{ctx.author.name}**, Oh no, something went wrong maybe you don\'t specify the current coin\nExample: {prefix}bitcoin EUR or {prefix}bitcoin USD')
        else:
            coin = coin.upper()
            request = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=BTC")
            bit_coin = request.json()['data']['rates'][coin] +  ' ' + str(c.get_symbol(coin))
            embed = discord.Embed(title='Bitcoin Currency', url='https://www.bitcoin.com', 
                description=f'Bitcoin value: {bit_coin}', timestamp=datetime.datetime.utcnow(), 
                color=discord.Color.blue())
            embed.set_thumbnail(url='https://logos-world.net/wp-content/uploads/2020/08/Bitcoin-Emblem.png')
            await ctx.send(embed=embed)
    except:
        await ctx.send(f'**{ctx.author.name}**, Oh no, something went wrong maybe you don\'t specify a real current coin\nExample: {prefix}bitcoin EUR or {prefix}bitcoin USD')

@bot.command()
async def convert(ctx, func : str, num : str=None):
    if func == 'binary':
        if num == None:
            await ctx.send(f'**{ctx.author.name}**, pls specify a binary number to convert in decimal')
        else:
            numero_decimal = 0
            for posicion, digito_string in enumerate(num[::-1]):
                numero_decimal += int(digito_string) * 2 ** posicion

            await ctx.send(f'**{ctx.author.name}**, {num} convert to decimal: {numero_decimal}')
    else:
        await ctx.send(f'**{ctx.author.name}**, Sorry the convert {func} doesn\'t exist')

@bot.command()
async def hack(ctx, member : discord.Member=None):
    if not member == None:
        user = member
    else:
        user = ctx.author

    if user.id == 781986435674406963:
        await ctx.send(f'Buen intento <@{ctx.author.id}> pero soy inhackebale')
    else:
        hack_msg = await ctx.send('Comenzando hackeo....')

        await hack_msg.edit(content='Comenzando hackeo...')
        for i in range(1):
            await hack_msg.edit(content='Comenzando hackeo...')
            await hack_msg.edit(content='Comenzando hackeo..')
        await hack_msg.edit(content='Comenzando hackeo...')

        if user.id == 658254360056168468:
            await hack_msg.edit(content=f'User: {user.name}\nPassword: {generate_password()}')
            await hack_msg.edit(content=f'User: {user.name}\nPassword: {generate_password()}\n<@{ctx.author.id}> Lo siento, lo he intentado\nPero no he podido hackear a <@{user.id}>')
        else:
            usernames = [user.name, str(user.name)[::-1], user.id, str(user.id)[::-1],
                str(user)[::-1][:4][::-1], str(user)[::-1][:4], user.id]

            for username in usernames:
                await hack_msg.edit(content=f'User: {username}\nPassword: {generate_password()}')
                await asyncio.sleep(0.6)

            await hack_msg.edit(content=f'User: {user.name}\nPassword: {generate_password()}\n<@{user.id}> Has sido hackeado con exito.')

def generate_password():
    lower = 'qwertyuiopasdfghjklzxcvbnm'
    upper = lower.upper()
    numbers = '123456789'
    symbols = '[]{}()*;/,._-'

    caracters = lower + upper + numbers + symbols
    length = 16

    password = ''.join(random.sample(caracters, length))
    return password

@bot.command()
async def kiss(ctx, user : discord.Member):
    image = random.sample(kiss_urls, 1)
    image = image[0]
    embed = discord.Embed(description=f'<@{ctx.author.id}> le dio un hermoso beso a <@{user.id}>', 
        timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.set_image(url=f'{image}')
    await ctx.send(embed=embed)

@bot.command()
async def wave(ctx, user : discord.Member):
    image = random.sample(wave_urls, 1)
    image = image[0]
    embed = discord.Embed(description=f'<@{user.id}>! <@{ctx.author.id}> te saludo! Esta contento de verte :D', 
        timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.set_image(url=f'{image}')
    await ctx.send(embed=embed)

@bot.command()
async def hug(ctx, user : discord.Member):
    if int(ctx.author.id) == int(user.id):
        embed = discord.Embed(color=discord.Color.blue(),
            description=f'<@{ctx.author.id}> Tan solo estas que te tienes que dar un abrazo tu mismo? :c')
        await ctx.send(embed=embed)
    else:
        image = random.sample(hug_urls, 1)
        image = image[0]
        embed = discord.Embed(description=f'<@{ctx.author.id}> abrazo a <@{user.id}>', 
            timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
        embed.set_image(url=f'{image}')
        await ctx.send(embed=embed)

@bot.command()
async def slap(ctx, user : discord.Member):
    image = random.sample(slap_urls, 1)
    image = image[0]
    embed = discord.Embed(description=f'<@{ctx.author.id}> le pego un buen putaso a <@{user.id}>, por lo visto se llevaban bien', 
        timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.set_image(url=f'{image}')
    await ctx.send(embed=embed)

@bot.command()
async def kill(ctx, user : discord.User):
    if int(ctx.author.id) == int(user.id):
        await ctx.send('Weee no te mates que arreamos a palos, tu vida es muy importante :c')
    else:
        image = random.sample(kill_urls, 1)
        image = image[0]
        embed = discord.Embed(description=f'<@{ctx.author.id}> mato a <@{user.id}>, por lo visto se llevaban bien', 
            timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
        embed.set_image(url=f'{image}')
        await ctx.send(embed=embed)

@bot.command()
async def pat(ctx, user : discord.Member):
    image = random.sample(pat_urls, 1)
    image = image[0]
    embed = discord.Embed(description=f'<@{ctx.author.id}> hizo pat pat a <@{user.id}>', 
        timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.set_image(url=f'{image}')
    await ctx.send(embed=embed)

@bot.command()
async def sleep(ctx):
    image = random.sample(sleep_urls, 1)
    image = image[0]
    embed = discord.Embed(description=f'Uy <@{ctx.author.id}> se ha dormido', 
        timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.set_image(url=f'{image}')
    await ctx.send(embed=embed)

@bot.command()
async def cry(ctx):
    image = random.sample(cry_urls, 1)
    image = image[0]
    embed = discord.Embed(description=f'<@{ctx.author.id}> esta llorando, necesita un abrazo :c', 
        timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.set_image(url=f'{image}')
    await ctx.send(embed=embed)

@bot.command()
async def sad(ctx):
    image = random.sample(cry_urls, 1)
    image = image[0]
    embed = discord.Embed(description=f'<@{ctx.author.id}> esta triste, necesita un abrazo :c', 
        timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.set_image(url=f'{image}')
    await ctx.send(embed=embed)

@bot.command()
async def smile(ctx):
    image = random.sample(happy_urls, 1)
    image = image[0]
    embed = discord.Embed(description=f'<@{ctx.author.id}> :D', 
        timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.set_image(url=f'{image}')
    await ctx.send(embed=embed)

@bot.command()
async def happy(ctx):
    image = random.sample(happy_urls, 1)
    image = image[0]
    embed = discord.Embed(description=f'<@{ctx.author.id}> esta feliz :D', 
        timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.set_image(url=f'{image}')
    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx, avamember : discord.Member=None):
    try:
        embed = discord.Embed(title=f'Avatar from {avamember.name}', url=f'{avamember.avatar_url}',
            description=f'User id: {avamember.id}', timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
        embed.set_image(url=f'{avamember.avatar_url}')
        await ctx.send(embed=embed)
    except:
        embed = discord.Embed(title=f'Avatar from {ctx.author.name}', url=f'{ctx.author.avatar_url}',
            description=f'User id: {ctx.author.id}', timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
        embed.set_image(url=f'{ctx.author.avatar_url}')
        await ctx.send(embed=embed)

def date_diference(fecha):
    x = fecha.split('-')
    then = datetime.datetime(int(x[0]), int(x[1]), int(x[2]))
    now = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
    delta = now - then
    return delta.days

@bot.command()
async def marry(ctx, user : discord.Member=None):
    if user == None:
        is_married = False
        for page in marrytable.get_iter():
            for record in page:
                days = date_diference(record["fields"]["Fecha"])
                if ctx.author.id == int(record['fields']['User']) and record['fields']['CheckBox'] == 'True':
                    embed = discord.Embed(title=f'{ctx.author.name}', description=f'<@{int(record["fields"]["Author"])}> se casó con <@{int(record["fields"]["User"])}> el **{record["fields"]["Fecha"]}**\nLlevan **{days} dias** juntos, que bonito es el amor <3', 
                        timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
                    embed.set_thumbnail(url=f'https://cdn.discordapp.com/emojis/590393335819272203.gif')
                    await ctx.send(embed=embed)
                    is_married = True
                elif ctx.author.id == int(record['fields']['Author']) and record['fields']['CheckBox'] == 'True':
                    embed = discord.Embed(title=f'{ctx.author.name}', description=f'<@{int(record["fields"]["Author"])}> se casó con <@{int(record["fields"]["User"])}> el **{record["fields"]["Fecha"]}**\nLlevan **{days} dias** juntos, que bonito es el amor <3', 
                        timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
                    embed.set_thumbnail(url=f'https://cdn.discordapp.com/emojis/590393335819272203.gif')
                    await ctx.send(embed=embed)
                    is_married = True

        if not is_married:
            await ctx.send(f'<@{ctx.author.id}> tienes que mencionar a un usuario para casarte con él/elle/ella\nejemplo: m!marry @user')
    else:
        if ctx.author.id == user.id:
            await ctx.send(f'<@{user.id}> Weee no puedes casarte contigo mismo o al menos desde la version **0.25.7** y estamos en la **{version}**')
        else:
            ids = []
            auth = []
            for page in marrytable.get_iter():
                for record in page:
                    ids.append(int(record['fields']['User']))
                    auth.append(int(record['fields']['Author']))

            if user.id in ids or user.id in auth:
                for page in marrytable.get_iter():
                    for record in page:
                        if user.id == int(record['fields']['User']) or user.id == int(record['fields']['Author']):
                            if record['fields']['CheckBox'] == 'False':
                                marrytable.delete(record['id'])
                                await ctx.send(f'<@{user.id}>, <@{ctx.author.id}> te ha pedido matrimonio\n Usa **m!am** para aceptarlo o **m!dm** para rechazarlo')
                                marrytable.insert({'Author': str(ctx.author.id), 'User': str(user.id), 'CheckBox': 'False'})
                            else:
                                await ctx.send(f'Lo siento mucho <@{ctx.author.id}> pero <@{user.id}> ya esta casado')
            elif ctx.author.id in auth or ctx.author.id in ids:
                for page in marrytable.get_iter():
                    for record in page:
                        if ctx.author.id == int(record['fields']['User']) or ctx.author.id == int(record['fields']['Author']):
                            if record['fields']['CheckBox'] == 'False':
                                marrytable.delete(record['id'])
                                await ctx.send(f'<@{user.id}>, <@{ctx.author.id}> te ha pedido matrimonio\n Usa **m!am** para aceptarlo o **m!dm** para rechazarlo')
                                marrytable.insert({'Author': str(ctx.author.id), 'User': str(user.id), 'CheckBox': 'False'})
                            else:
                                await ctx.send(f'<@{ctx.author.id}> no seas mamón y antes de pedirle matrimonia a alguien divorciate con el m!divorce')
            else:
                await ctx.send(f'<@{user.id}>, <@{ctx.author.id}> te ha pedido matrimonio\n Usa **m!am** para aceptarlo o **m!dm** para rechazarlo')
                marrytable.insert({'Author': str(ctx.author.id), 'User': str(user.id), 'CheckBox': 'False'})

@bot.command()
async def am(ctx):
    image = random.sample(kiss_urls, 1)
    image = image[0]
    for page in marrytable.get_iter():
        for record in page:
            if ctx.author.id == int(record['fields']['User']) and record['fields']['CheckBox'] == 'False':
                fields = {'Author': record['fields']['Author'], 'User': str(ctx.author.id), 'CheckBox': 'True'}
                marrytable.replace(record['id'], fields)
                embed = discord.Embed(title=f'Boda en {ctx.guild.name}', description=f'Estamos presenciando un bonito momento en el cual se casan <@{ctx.author.id}> y <@{record["fields"]["Author"]}>\nPasemos a contemplar el supuesto "primer" beso:', 
                    timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
                embed.set_image(url=f'{image}')
                await ctx.send(embed=embed)
                await ctx.send('VIVAN LES NOVIES!!!')

@bot.command()
async def dm(ctx):
    for page in marrytable.get_iter():
        for record in page:
            if ctx.author.id == int(record['fields']['User']) and record['fields']['CheckBox'] == 'False':
                await ctx.send(f'Vaya que pena al final fue un desastre de boda :c')
                record = marrytable.match('User', ctx.author.id)
                marrytable.delete(record['id'])

@bot.command()
async def divorce(ctx):
    is_married = False
    for page in marrytable.get_iter():
        for record in page:
            if ctx.author.id == int(record['fields']['User']):
                await ctx.send(f'<@{ctx.author.id}> se divorcio de <@{int(record["fields"]["User"])}> :c')
                record = marrytable.match('User', ctx.author.id)
                marrytable.delete(record['id'])
                is_married = True
            elif ctx.author.id == int(record['fields']['Author']):
                await ctx.send(f'<@{ctx.author.id}> se divorcio de <@{int(record["fields"]["User"])}> :c')
                record = marrytable.match('author', ctx.author.id)
                marrytable.delete(record['id'])
                is_married = True

    if not is_married:
        await ctx.send(f'<@{ctx.author.id}> para divorciarse primero tienes que estar casade')

@bot.command()
async def marrystatus(ctx, user : discord.Member=None):
    if user == None:
        user = ctx.author

    is_married = False
    for page in marrytable.get_iter():
        for record in page:
            days = date_diference(record["fields"]["Fecha"])
            if user.id == int(record['fields']['User']) and record['fields']['CheckBox'] == 'True':
                embed = discord.Embed(title=f'{user.name}', description=f'<@{int(record["fields"]["Author"])}> se casó con <@{int(record["fields"]["User"])}> el **{record["fields"]["Fecha"]}**\nLlevan **{days} dias** juntos, que bonito es el amor <3', 
                    timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
                embed.set_thumbnail(url=f'https://cdn.discordapp.com/emojis/590393335819272203.gif')
                await ctx.send(embed=embed)
                is_married = True
            elif user.id == int(record['fields']['Author']) and record['fields']['CheckBox'] == 'True':
                embed = discord.Embed(title=f'{user.name}', description=f'<@{int(record["fields"]["Author"])}> se casó con <@{int(record["fields"]["User"])}> el **{record["fields"]["Fecha"]}**\nLlevan **{days} dias** juntos, que bonito es el amor <3', 
                    timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
                embed.set_thumbnail(url=f'https://cdn.discordapp.com/emojis/590393335819272203.gif')
                await ctx.send(embed=embed)
                is_married = True
    
    if not is_married:
        if ctx.author.id == user.id:
            await ctx.send(f'<@{user.id}> Si quieres ver tu status de casade, que tal si primero te casas con alguien??')
        else:
            await ctx.send(f'<@{ctx.author.id}> no podemos ver le estatus de casade de alguien que no esta casade, DUH!')

def insert_returns(body):

    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

def insert_returns(body):

    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


class admin(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
    
    @commands.command(pass_context=True)
    async def eval(self, ctx, *, cmd):
        if ctx.author.id == 658254360056168468:
            fn_name = "_eval_expr"

            cmd = "\n".join(f"    {i}" for i in cmd.splitlines    ())

            # wrap in async def body
            body = f"async def {fn_name}():\n{cmd}"

            parsed = ast.parse(body)
            body = parsed.body[0].body

            insert_returns(body)

            env = {
                'client': ctx.bot,
                'bot': ctx.bot,
                'discord': discord,
                'commands': commands,
                'ctx': ctx,
                'requests': requests,
                'os': os,
                '__import__': __import__,
                'asyncio': asyncio,
                'ast': ast    
            }

            exec(compile(parsed, filename="<ast>",    mode="exec"), env)

            try:
                result = (await eval(f"{fn_name}()", env))
                if result == None:
                    return
                await ctx.send(f'```py\n{result}```')
            except Exception as error:
                await ctx.send(f'```\n{error}```')

bot.add_cog(admin(bot))

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(name='Ser Dios', url='https://discord.com'))
    print('My Bot is Ready')

bot.run(str(token))