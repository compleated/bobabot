import asyncio
import json
import time

import discord
from discord.utils import get

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents, heartbeat_timeout=6000)

FOUR_WEEKS_SECONDS = 60 * 60 * 24 * 28

@client.event
async def on_guild_available(guild):
    current_time = int(time.time())
    print("Logged in as %s on %s at %d" % (client.user, guild.name, current_time))

    active_role = get(guild.roles, name="Active30")
    inactive_role = get(guild.roles, name="Inactive")
    member_role = get(guild.roles, name="BOBAes")
    bot_role = get(guild.roles, name="Bot")

    # HX: Fix writing on initial run
    with open("member_activity/%s.json" % guild.id, "r") as f:
        contents = f.read()
        if contents:
            member_activity = json.loads(contents)
        else:
            member_activity = {}

        for member in guild.members:
            if member.get_role(bot_role.id):
                continue
            # HX: Only remove if member is not longer X
            if member.get_role(inactive_role.id):
                last_seen_time = member_activity.get(str(member.id), 0)
                if last_seen_time:
                    if current_time - last_seen_time > FOUR_WEEKS_SECONDS:
                        await guild.kick(member)
                        print("Inactive member kicked (%s)" % member) 
            elif not member.get_role(active_role.id) and member.get_role(member_role.id):
                member_activity[member.id] = current_time
                await member.remove_roles(member_role,
                                          reason="Member role removed for inactivity.")
                print("Member role successfully removed from %s" % member)
                await member.add_roles(inactive_role,
                                       reason="Inactive role added for inactivity.")
                print("Inactive role successfully added to %s" % member)
            elif member.get_role(active_role.id):
                try:
                    del member_activity[member.id]
                except KeyError:
                    0

    with open("member_activity/%s.json" % guild.id, "w") as f:
        f.write(json.dumps(member_activity))

with open('secrets', 'r') as f:
    token = f.read().strip('\n')
client.run(token)
