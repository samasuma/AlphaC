import yaml
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests
from datetime import datetime
from pytz import timezone

def load_config():
    with open('config.yml', 'r') as f:
        return yaml.safe_load(f)

config = load_config()

TELEGRAM_BOT_TOKEN = config['telegram']['bot_token']
# Note: The chat_id might not be necessary for the bot functionality you've described
CHAT_ID = config['telegram']['chat_id']
# As of my last update, CoinGecko API does not require an API key for public data, so this might not be used
COINGECKO_API_KEY = config.get('coingecko', {}).get('api_key', None)

def get_coin_id(symbol):
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url).json()
    
    for coin in response:
        if coin['symbol'].lower() == symbol.lower():
            return coin['id']
    return None

def get_coin_info(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    response = requests.get(url).json()
    
    name = response.get('name')
    symbol = response.get('symbol').upper()
    current_price = response['market_data']['current_price']['usd']
    price_change_percentage_24h = response['market_data']['price_change_percentage_24h_in_currency']['usd']
    total_volume_24h = response['market_data']['total_volume']['usd']
    market_cap = response['market_data']['market_cap']['usd']
    cst_time = datetime.now(timezone('America/Chicago')).strftime('%Y-%m-%d %H:%M:%S')

    price_emoji = "🔺" if price_change_percentage_24h >= 0 else "🔻"
    
    message = (f"{name} ({symbol})\n"
               f"Current Price: ${current_price:,.2f}\n"
               f"24h Change: {price_emoji}{abs(price_change_percentage_24h):.2f}%\n"
               f"24h Volume (USD): ${total_volume_24h:,.2f}\n"
               f"Market Cap (USD): ${market_cap:,.2f}\n"
               f"Current Time: {cst_time}")
    
    return message

def coin_info(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        update.message.reply_text("Please provide a coin symbol. Usage: /coin_info <symbol>")
        return
    
    symbol = context.args[0]
    coin_id = get_coin_id(symbol)
    
    if coin_id:
        info = get_coin_info(coin_id)
        update.message.reply_text(info)
    else:
        update.message.reply_text("Coin not found.")

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler('coin_info', coin_info))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
