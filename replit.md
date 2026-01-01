# Telegram Trading Signals Bot

## Overview
A Telegram bot that provides trading signals. Users must authenticate with a password before accessing bot features.

## Project Structure
- `Python.py` - Main bot application
- `requirements.txt` - Python dependencies

## Environment Variables Required
- `BOT_TOKEN` - Telegram Bot API token (required)
- `BOT_PASSWORD` - Password for user authentication (defaults to "15031995Sinok")

## Dependencies
- python-telegram-bot==20.7

## Running the Bot
The bot runs via polling and does not expose any web interface.

## Features
- Password-protected access
- Trading signals display (EUR/USD example)
- Settings menu (placeholder)

## Setup Instructions
1. Get a bot token from @BotFather on Telegram
2. Set the `BOT_TOKEN` environment variable/secret
3. Optionally set a custom `BOT_PASSWORD`
4. Run the bot
