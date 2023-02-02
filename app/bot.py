import discord
import asyncio
import json
import re
#from discord.ext import tasks
import json
import configs.secrets

config = {}

def stripTeamName(name):
    result = 'team_'
    for c in name:
        if c.isalnum():
            result += c.lower()
        elif result and not result.endswith('_'):
            result += '_'

    if result.endswith('_'):
        result = result[:-1]
    return result

async def createTeam(team_name, message, category_name ):
    global config
    team_name = stripTeamName(team_name)

    category = discord.utils.get(message.guild.categories, name=category_name)
    role = await message.guild.create_role(name=team_name)
    channel = await message.guild.create_text_channel(name=team_name, category=category)

    config[str(message.guild.id)]["channels"][channel.id] = {}
    config[str(message.guild.id)]["channels"][channel.id]['owner'] = message.author.id

    json.dump(config, open('./configs/config.json', 'w'))
    config = json.load(open('./configs/config.json'))

    await channel.set_permissions(role, read_messages=True)
    await channel.edit(topic =(f"Owner: @{message.author.name}"))
    await message.author.add_roles(role)

    return channel

async def removeTeam(message):
    global config
    if(config[str(message.guild.id)]["channels"][str(message.channel.id)]["owner"] == message.author.id):
        role =  discord.utils.get(message.guild.roles, name=message.channel.name)
        await role.delete()
        await message.channel.delete()
        config[str(message.guild.id)]["channels"].pop(str(message.channel.id))
        json.dump(config, open('./configs/config.json', 'w',))
    else:
        owner_id = (config[str(message.guild.id)]["channels"][str(message.channel.id)]["owner"])
        await message.channel.send(f"only <@{owner_id}> can use this command!")

async def renameTeam(team_name, message):
    global config
    team_name = stripTeamName(team_name)

    if(config[str(message.guild.id)]["channels"][str(message.channel.id)]["owner"] == message.author.id):
        old_chanel = message.channel
        old_chanel_name = old_chanel.name
        old_role =  discord.utils.get(message.guild.roles, name=old_chanel.name)
        await old_chanel.edit(name = team_name)
        await old_role.edit(name = team_name)
        await message.channel.send(f"Renamed #{old_chanel_name} to <#{old_chanel.id}> !")
    else:
        owner_id = (config[str(message.guild.id)]["channels"][str(message.channel.id)]["owner"])
        await message.channel.send(f"only <@{owner_id}> can use this command!")

async def sendHelp(message ):
    helpMsg = "**Available commands:**\n"
    helpMsg += "/help - displays this message"
    helpMsg += "/team create [team_name] - creates a new role and text channel\n"

    if (await isGuildAdmin(message) == True):
        helpMsg += "\n"
        helpMsg += "**Administrator Commands:**\n"
        helpMsg += "/settings set [settings_key] [settings_value] - change option value\n"
        helpMsg += "/category [new_category_name] - create category\n"

    helpMsg += "\n"
    helpMsg += "**Available inside Team Channel:**\n"
    helpMsg += "/delete - delete team\n"
    helpMsg += "/rename [new_team_name] - rename team\n"
    helpMsg += "/invite [user_name] - invite user to team chanel\n"
    helpMsg += "/remove [user_name] - remove user from team chanel\n"
    helpMsg += "/owner [user_name] - change owner of team chanel\n"

    await message.channel.send(helpMsg)

async def inviteToTeam(user_name, message):
    if(config[str(message.guild.id)]["channels"][str(message.channel.id)]["owner"] == message.author.id):
        user_obj =  discord.utils.get(message.guild.members, name=user_name)
        role =  discord.utils.get(message.guild.roles, name=message.channel.name)
        await user_obj.add_roles(role)
        await message.channel.send(f"Welcome <@{user_obj.id}> !")
    else:
        owner_id = (config[str(message.guild.id)]["channels"][str(message.channel.id)]["owner"])
        await message.channel.send(f"only <@{owner_id}> can use this command!")

async def removeFromTeam(user_name, message):
    if(config[str(message.guild.id)]["channels"][str(message.channel.id)]["owner"] == message.author.id):
        user_obj =  discord.utils.get(message.guild.members, name=user_name)
        role =  discord.utils.get(message.guild.roles, name=message.channel.name)
        await user_obj.remove_roles(role)
        await message.channel.send(f"<@{user_obj.id}> Removed!")
    else:
        owner_id = (config[str(message.guild.id)]["channels"][str(message.channel.id)]["owner"])
        await message.channel.send(f"only <@{owner_id}> can use this command!")

async def isGuildAdmin(message):
    for permission in message.author.guild_permissions:
        if (permission[0] == 'administrator' and permission[1] == True):
            return True

    return False

async def changeSettingsValue(message, key,value):
    global config

    print('key:' + key)
    print('value:' + value)

    config[str(message.guild.id)][str(key)] = value
    json.dump(config, open('./configs/config.json', 'w'))
    config = json.load(open('./configs/config.json'))
    await message.channel.send(f"Settings modified !")

async def createCategory(category_name, message):
    category_obj = discord.utils.get(message.guild.categories, name=category_name)

    if category_obj is None: #If there's no category matching with the `name`
        await message.guild.create_category(category_name) #Creates the category

async def changeOwner(user_name, message):
    global config

    if(config[str(message.guild.id)]["channels"][str(message.channel.id)]["owner"] == message.author.id):
        user_obj =  discord.utils.get(message.guild.members, name=user_name)
        config[str(message.guild.id)]["channels"][str(message.channel.id)]["owner"] = user_obj.id
        await message.channel.edit(topic =(f"Owner: @{user_obj.name}"))

        json.dump(config, open('./configs/config.json', 'w'))
        config = json.load(open('./configs/config.json'))
        await message.channel.send(f"<@{user_obj.id}> is new owner!")
    else:
        owner_id = (config[str(message.guild.id)]["channels"][str(message.channel.id)]["owner"])
        await message.channel.send(f"only <@{owner_id}> can use this command!")

# @tasks.loop(minutes=1)
# async def statsUpdate():
#     channel = client.get_channel(1069881624168255539)
#     await channel.send("statsUpdate")

# print('Servers connected to:')
# for guild in client.guilds:
#     print(guild.name)
#     print(guild.id)
    # for category in guild.categories:
    #     print(category.name)

#statsUpdate.start()

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    global config
    config = json.load(open('./configs/config.json'))
    print(f'Bot is ready Bot name: @{client.user.name}')

@client.event
async def on_guild_join(guild):
    global config

    if (str(guild.id) in config):
        return

    config[str(guild.id)] = {"channels":{}}
    json.dump(config, open('./configs/config.json', 'w'))
    config = json.load(open('./configs/config.json'))

@client.event
async def on_message(message):
    global config

    # Ignore Command send by BOT
    if message.author == client.user:
        return

    # Ordinary message handling
    createCommandPerfix = f"@{client.user.name} "
    config = json.load(open('./configs/config.json'))

    #Teams Commands Section
    teamCreateCommand = f"{createCommandPerfix}/team create "
    if message.clean_content.startswith(teamCreateCommand):
        team_name = message.clean_content[len(teamCreateCommand):]
        channel = await createTeam(team_name, message, config[str(message.guild.id)]["new_teams_channel"])
        await message.channel.send(f"<@{message.author.id}> Channel <#{channel.id}> created!")
        return

    deleteCommand = f"{createCommandPerfix}/delete"
    if message.clean_content.startswith(deleteCommand):
        await removeTeam(message)
        return

    renameCommand = f"{createCommandPerfix}/rename "
    if message.clean_content.startswith(renameCommand):
        team_name = message.clean_content[len(renameCommand):].split("#")[0]
        await renameTeam(team_name, message)
        return

    inviteCommand = f"{createCommandPerfix}/invite "
    if message.clean_content.startswith(inviteCommand):
        user_name = message.clean_content[len(inviteCommand):].split("#")[0]
        await inviteToTeam(user_name, message)
        return

    removeMemberCommand = f"{createCommandPerfix}/remove "
    if message.clean_content.startswith(removeMemberCommand):
        user_name = message.clean_content[len(removeMemberCommand):].split("#")[0]
        await removeFromTeam(user_name, message)
        return

    changeOwnerCommand = f"{createCommandPerfix}/owner "
    if message.clean_content.startswith(changeOwnerCommand):
        user_name = message.clean_content[len(changeOwnerCommand):].split("#")[0]
        await changeOwner(user_name, message)
        return

    settingsCommand = f"{createCommandPerfix}/settings set "
    if message.clean_content.startswith(settingsCommand):
        if (await isGuildAdmin(message) == False):
            await message.channel.send(f"You are not server Administrator!")
            return

        key, value = message.clean_content[len(settingsCommand):].split()
        await changeSettingsValue(message, key, value)
        return

    helpCommand = f"{createCommandPerfix}/help"
    if message.clean_content.startswith(helpCommand):
        await sendHelp(message)
        return

    #Utils Commands Section
    teamCategoryCommand = f"{createCommandPerfix}/category create "
    if message.clean_content.startswith(teamCategoryCommand):
        if (await isGuildAdmin(message) == False):
            await message.channel.send(f"You are not server Administrator!")
            return

        category_name = message.clean_content[len(teamCategoryCommand):]
        createCategory(category_name, message)
        return

client.run(secrets.API_KEY)
