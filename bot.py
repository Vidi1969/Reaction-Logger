
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_FILE = "reaction_log_channel.txt"

intents = discord.Intents.default()
intents.message_content = True  # Needed for commands
intents.reactions = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

def save_channel_id(channel_id):
    print(f"DEBUG: Saving channel_id {channel_id} to {CHANNEL_FILE}")
    with open(CHANNEL_FILE, "w", encoding="utf-8") as f:
        f.write(str(channel_id))
    print(f"DEBUG: Saved channel_id {channel_id}")

def load_channel_id():
    print(f"DEBUG: Loading channel_id from {CHANNEL_FILE}")
    if os.path.exists(CHANNEL_FILE):
        with open(CHANNEL_FILE, "r", encoding="utf-8") as f:
            value = f.read().strip()
            print(f"DEBUG: Read value from file: {value}")
            try:
                return int(value)
            except Exception as e:
                print(f"DEBUG: Error converting value to int: {e}")
                return None
    print("DEBUG: Channel file does not exist")
    return None
@bot.event
async def on_raw_reaction_remove(payload):
    print(f"DEBUG: on_raw_reaction_remove fired: emoji={payload.emoji} user_id={payload.user_id} message_id={payload.message_id}")
    # Try to fetch the channel and message
    channel = bot.get_channel(payload.channel_id)
    if not channel:
        print(f"DEBUG: Could not get channel for id {payload.channel_id}")
        return
    try:
        message = await channel.fetch_message(payload.message_id)
        print(f"DEBUG: Successfully fetched message {payload.message_id}")
    except Exception as e:
        print(f"DEBUG: Could not fetch message: {e}")
        return
    user = bot.get_user(payload.user_id)
    if not user:
        try:
            user = await bot.fetch_user(payload.user_id)
            print(f"DEBUG: Successfully fetched user {payload.user_id}")
        except Exception as e:
            print(f"DEBUG: Could not fetch user: {e}")
            return
    # Create a fake reaction object for logging
    class FakeReaction:
        def __init__(self, emoji, message):
            self.emoji = emoji
            self.message = message
    fake_reaction = FakeReaction(payload.emoji, message)
    await send_reaction_log_embed("removed", fake_reaction, user)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command(name="reactlog", aliases=["react-log"])
async def set_react_log(ctx, channel: discord.TextChannel):
    save_channel_id(channel.id)
    await ctx.send(f"Reaction log channel set to {channel.mention}")

# Optional: Give user feedback if command is not found
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Unknown command. Try !reactlog #channel or !react-log #channel.")
    else:
        raise error

async def send_reaction_log_embed(event_type, reaction, user):
    channel_id = load_channel_id()
    if not channel_id:
        return
    channel = bot.get_channel(channel_id)
    if not channel:
        return
    action = "added" if event_type == "added" else "removed"
    embed = discord.Embed(
        title=f"Reaction {action}",
        color=0x00ff00
    )
    embed.add_field(name="User", value=user.mention, inline=True)
    embed.add_field(name="Emoji", value=str(reaction.emoji), inline=True)
    embed.add_field(name="Message", value=f"[Jump to message]({reaction.message.jump_url})", inline=False)
    embed.set_footer(text=f"{discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    await channel.send(embed=embed)



# Unified handler for both add and remove using raw events
async def log_reaction_event(payload, removed):
    # Ignore bots
    user = bot.get_user(payload.user_id)
    if not user:
        try:
            user = await bot.fetch_user(payload.user_id)
        except Exception as e:
            print(f"DEBUG: Could not fetch user: {e}")
            return
    if getattr(user, 'bot', False):
        print(f"DEBUG: Ignoring bot reaction from {user}")
        return
    channel = bot.get_channel(payload.channel_id)
    if not channel:
        print(f"DEBUG: Could not get channel for id {payload.channel_id}")
        return
    try:
        message = await channel.fetch_message(payload.message_id)
        print(f"DEBUG: Successfully fetched message {payload.message_id}")
    except Exception as e:
        print(f"DEBUG: Could not fetch message: {e}")
        return
    # Compose embed
    action = "Removed" if removed else "Added"
    channel_id = load_channel_id()
    if not channel_id:
        print("DEBUG: No log channel set")
        return
    log_channel = bot.get_channel(channel_id)
    if not log_channel:
        print(f"DEBUG: Could not get log channel for id {channel_id}")
        return
    content = message.content or "*(no content)*"
    embed = discord.Embed(
        title=f"Reaction {action}",
        color=0x00ff00
    )
    # Add fields with spacing using zero-width space (\u200b)
    embed.add_field(name="👤 User", value=user.mention, inline=True)
    embed.add_field(name="🙂 Emoji", value=str(payload.emoji), inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)  # Spacer

    embed.add_field(name="📺 Channel", value=f"<#{payload.channel_id}>", inline=True)
    embed.add_field(name="🔗 Jump", value=f"[Jump to Message](https://discord.com/channels/{payload.guild_id}/{payload.channel_id}/{payload.message_id})", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)  # Spacer

    embed.add_field(name="💬 Message Content", value=f"`{content}`", inline=True)
    embed.add_field(name="📝 Message ID", value=str(payload.message_id), inline=False)

    embed.set_footer(text=f"{discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    await log_channel.send(embed=embed)
    print(f"DEBUG: Sent embed for reaction {action.lower()} by {user} on message {payload.message_id}")

@bot.event
async def on_raw_reaction_add(payload):
    print(f"DEBUG: on_raw_reaction_add fired: emoji={payload.emoji} user_id={payload.user_id} message_id={payload.message_id}")
    await log_reaction_event(payload, removed=False)

@bot.event
async def on_raw_reaction_remove(payload):
    print(f"DEBUG: on_raw_reaction_remove fired: emoji={payload.emoji} user_id={payload.user_id} message_id={payload.message_id}")
    await log_reaction_event(payload, removed=True)

if __name__ == "__main__":
    bot.run(TOKEN)
