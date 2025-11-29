# Reaction Logger Discord Bot

This is a simple Discord bot written in Python that logs the adding and removal of reactions to messages on a Discord server.

## Features
- Logs when a reaction is added to or removed from any message.
- Uses `discord.py` and `python-dotenv` for environment variable management.

## Setup
1. **Clone or download this repository.**
2. **Create a virtual environment (optional but recommended):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
4. **Create a `.env` file in the project root with your bot token:**
   ```env
   DISCORD_TOKEN=your_token_here
   ```
5. **Run the bot:**
   ```powershell
   python bot.py
   ```

## Security
- The `.env` file is included in `.gitignore` and will not be committed to version control.
- **Never share your Discord bot token publicly.**

## Requirements
- Python 3.8+
- `discord.py`
- `python-dotenv`

---

Replace `your_token_here` in the `.env` file with your actual Discord bot token.
