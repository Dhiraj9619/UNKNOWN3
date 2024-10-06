import http.client
import json
import random
import string
import time
import signal
import sys
import ssl
import socket
import os  # For clearing the terminal
from urllib.parse import unquote
from colorama import Fore, Style

# Import the modules directly since they are now in the main directory
from headers import headers_set
from queries import QUERY_USER, MUTATION_GAME_PROCESS_TAPS_BATCH, QUERY_BOOSTER, QUERY_NEXT_BOSS, QUERY_GAME_CONFIG

url = "api-gw-tg.memefi.club"

# Function to fetch IP and country
def get_ip_and_country():
    try:
        conn = http.client.HTTPSConnection("ipinfo.io")
        conn.request("GET", "/json")
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        conn.close()
        info = json.loads(data)
        ip = info.get("ip", "Unknown")
        country = info.get("country", "Unknown")
        return ip, country
    except Exception as e:
        print(f"Failed to get IP and country info: {e}")
        return "Unknown", "Unknown"

# Art function with connection information
def art():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.GREEN + Style.BRIGHT + r"""
  _                
 | | | |             | |               
 | |_| |  __ _   ___ | | __  ___  _ __ 
 |  _  | / _` | / __|| |/ / / _ \| '__|
 | | | || (_| || (__ |   < |  __/| |   
 \_| |_/ \__,_| \___||_|\_\ \___||_| 
    """ + Style.RESET_ALL)
    
    # Get IP and country
    ip, country = get_ip_and_country()
    print(Fore.CYAN + "MemeFi Script Edited by TG @Dhiraj_9619 💣 " + Style.RESET_ALL)
    print(Fore.MAGENTA + f"[ ip : {ip} | country: {country} ]" + Style.RESET_ALL)
    print(Fore.YELLOW + "=" * 43 + Style.RESET_ALL)

# Handle Ctrl+C gracefully
def signal_handler(sig, frame):
    print("\nExiting gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def safe_post(url, headers, json_payload):
    retries = 5
    timeout = 10  # Timeout in seconds for each connection attempt
    context = ssl.create_default_context()
    for attempt in range(retries):
        try:
            conn = http.client.HTTPSConnection(url, timeout=timeout, context=context)
            payload = json.dumps(json_payload)
            conn.request("POST", "/graphql", payload, headers)
            res = conn.getresponse()
            response_data = res.read().decode("utf-8")
            conn.close()  # Ensure connection is closed
            if res.status == 200:
                return json.loads(response_data)  # Return the JSON response if successful
            else:
                print(f"🎯 Failed with status {res.status}, retrying...")
        except (http.client.HTTPException, TimeoutError, ConnectionError, ssl.SSLEOFError, ssl.SSLError) as e:
            print(f"🎯 Network Error: {e}, retrying...")
        except socket.gaierror as e:
            print(f"🎯 Address Resolution Error: {e}, retrying...")
        time.sleep(3)  # Wait before retrying
    print("🎯 Failed after several attempts.")
    return None

def generate_random_nonce(length=52):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Get access token
def fetch(account_line):
    with open('query_id.txt', 'r') as file:
        lines = file.readlines()
        raw_data = lines[account_line - 1].strip()

    tg_web_data = unquote(unquote(raw_data))
    query_id = tg_web_data.split('query_id=', maxsplit=1)[1].split('&user', maxsplit=1)[0]
    user_data = tg_web_data.split('user=', maxsplit=1)[1].split('&auth_date', maxsplit=1)[0]
    auth_date = tg_web_data.split('auth_date=', maxsplit=1)[1].split('&hash', maxsplit=1)[0]
    hash_ = tg_web_data.split('hash=', maxsplit=1)[1].split('&', maxsplit=1)[0]

    user_data_dict = json.loads(unquote(user_data))

    url = 'api-gw-tg.memefi.club'
    headers = headers_set.copy()  # Use headers from utils/headers.py
    data = {
        "operationName": "MutationTelegramUserLogin",
        "variables": {
            "webAppData": {
                "auth_date": int(auth_date),
                "hash": hash_,
                "query_id": query_id,
                "checkDataString": f"auth_date={auth_date}\nquery_id={query_id}\nuser={unquote(user_data)}",
                "user": {
                    "id": user_data_dict["id"],
                    "allows_write_to_pm": user_data_dict["allows_write_to_pm"],
                    "first_name": user_data_dict["first_name"],
                    "last_name": user_data_dict["last_name"],
                    "username": user_data_dict.get("username", "Username not set"),
                    "language_code": user_data_dict["language_code"],
                    "version": "7.2",
                    "platform": "ios",
                    "is_premium": user_data_dict.get("is_premium", False)
                }
            }
        },
        "query": "mutation MutationTelegramUserLogin($webAppData: TelegramWebAppDataInput!) {\n  telegramUserLogin(webAppData: $webAppData) {\n    access_token\n    __typename\n  }\n}"
    }

    context = ssl.create_default_context()
    conn = http.client.HTTPSConnection(url, context=context, timeout=10)  # Add timeout for fetch
    try:
        payload = json.dumps(data)
        conn.request("POST", "/graphql", payload, headers)
        res = conn.getresponse()
        response_data = res.read().decode("utf-8")
        if res.status == 200:
            try:
                json_response = json.loads(response_data)
                if 'errors' in json_response:
                    return None
                else:
                    access_token = json_response['data']['telegramUserLogin']['access_token']
                    return access_token
            except json.JSONDecodeError:
                print("Failed to decode JSON response")
                return None
        else:
            return None
    except (http.client.HTTPException, ssl.SSLEOFError, ssl.SSLError) as e:
        print(f"🎯 SSL Error during fetch: {e}")
        return None
    finally:
        conn.close()

# Check access token
def cek_user(index):
    access_token = fetch(index + 1)
    url = "api-gw-tg.memefi.club"

    headers = headers_set.copy()  # Make a copy of headers_set to avoid modifying the global variable
    headers['Authorization'] = f'Bearer {access_token}'

    json_payload = {
        "operationName": "QueryTelegramUserMe",
        "variables": {},
        "query": QUERY_USER
    }

    response = safe_post(url, headers, json_payload)
    if response and 'errors' not in response:
        user_data = response['data']['telegramUserMe']
        return user_data  # Return the response result
    else:
        print(f"🎯 Failed with status {response}")
        return None  # Return None if an error occurs

def activate_booster(index, headers):
    access_token = fetch(index + 1)
    url = "api-gw-tg.memefi.club"
    print("\r🎯 Activating Turbo Boost ... ", end="", flush=True)

    headers = headers_set.copy()  # Make a copy of headers_set to avoid modifying the global variable
    headers['Authorization'] = f'Bearer {access_token}'

    recharge_booster_payload = {
        "operationName": "telegramGameActivateBooster",
        "variables": {"boosterType": "Turbo"},
        "query": QUERY_BOOSTER
    }

    response = safe_post(url, headers, recharge_booster_payload)
    if response and 'data' in response:
        current_health = response['data']['telegramGameActivateBooster']['currentBoss']['currentHealth']
        return current_health  # Return current boss health
    else:
        print(f"🎯 Failed to activate booster, retrying...")
        return None

def submit_taps(index, json_payload):
    access_token = fetch(index + 1)
    url = "api-gw-tg.memefi.club"

    headers = headers_set.copy()
    headers['Authorization'] = f'Bearer {access_token}'

    response = safe_post(url, headers, json_payload)
    if response:
        return response  # Ensure to return already parsed data
    else:
        print(f"🎯 Failed to tap, retrying...")
        return None  # Return None if an error occurs

def set_next_boss(index, headers):
    access_token = fetch(index + 1)
    url = "api-gw-tg.memefi.club"

    headers = headers_set.copy()  # Make a copy of headers_set to avoid modifying the global variable
    headers['Authorization'] = f'Bearer {access_token}'
    boss_payload = {
        "operationName": "telegramGameSetNextBoss",
        "variables": {},
        "query": QUERY_NEXT_BOSS
    }

    response = safe_post(url, headers, boss_payload)
    if response and 'data' in response:
        print("✅ Successfully changed boss.", flush=True)
    else:
        print("🎯 Failed to change boss.", flush=True)

# Check stats
def cek_stat(index, headers):
    access_token = fetch(index + 1)
    url = "api-gw-tg.memefi.club"

    headers = headers_set.copy()  # Make a copy of headers_set to avoid modifying the global variable
    headers['Authorization'] = f'Bearer {access_token}'

    json_payload = {
        "operationName": "QUERY_GAME_CONFIG",
        "variables": {},
        "query": QUERY_GAME_CONFIG
    }

    response = safe_post(url, headers, json_payload)
    if response and 'errors' not in response:
        user_data = response['data']['telegramGameGetConfig']
        return user_data
    else:
        print(f"🎯 Failed with status {response}")
        return None  # Return None if an error occurs

def main():
    # Display art
    art()

    # Ask if ready for the script
    ready = input("will you use in your fake account ? (y/n): ").strip().lower()
    if ready != 'y':
        print("Exiting...")
        return

    turbo_booster = 'n'  # Default value
    god_mode = 'n'  # Default value
    while True:  # Continue running the script
        try:
            # Ask for Turbo Booster and God Mode options only once
            if turbo_booster == 'n' or god_mode == 'n':
                while True:
                    turbo_booster = input("Use Turbo Booster (default n) ? (y/n): ").strip().lower()
                    if turbo_booster in ['y', 'n', '']:
                        turbo_booster = turbo_booster or 'n'
                        break
                    else:
                        print("Enter 'y' or 'n'.")

                if turbo_booster == 'y':
                    while True:
                        god_mode = input("Activate God Mode (1x tap monster dead) ? (y/n): ").strip().lower()
                        if god_mode in ['y', 'n', '']:
                            god_mode = god_mode or 'n'
                            break
                        else:
                            print("Enter 'y' or 'n'.")

            print("Starting Memefi bot...")
            print("\r Getting valid account list...", end="", flush=True)

            with open('query_id.txt', 'r') as file:
                lines = file.readlines()

            # Collect account information first
            accounts = []
            for index, line in enumerate(lines):
                result = cek_user(index)
                if result is not None:
                    first_name = result.get('firstName', 'Unknown')
                    last_name = result.get('lastName', 'Unknown')
                    league = result.get('league', 'Unknown')
                    accounts.append((index, result, first_name, last_name, league))
                else:
                    print(f"🎯 Account {index + 1}: Token invalid or error occurred")

            # Display account list
            print("\rAccount list:                                   ", flush=True)
            for index, _, first_name, last_name, league in accounts:
                print(f"🎯 [ Account {first_name} {last_name} ] | League 🎯 {league}")

            # Process each account
            for index, result, first_name, last_name, league in accounts:
                print(f"\r[ Account {index + 1} ] {first_name} {last_name} checking tasks...", end="", flush=True)
                headers = {'Authorization': f'Bearer {result}'}

                while True:  # Keep defeating bosses until Turbo Boost is empty
                    stat_result = cek_stat(index, headers)

                    if stat_result is not None:
                        user_data = stat_result
                        if user_data['freeBoosts']['currentTurboAmount'] <= 0:
                            print("\n🎯 Turbo Boost is not available. Moving to next account.")
                            break  # Exit the inner while loop to move to the next account

                        output = (
                            f"[ Account {index + 1} - {first_name} {last_name} ]\n"
                            f"Coin 🪙  {user_data['coinsAmount']:,}\n"
                            f"Level 🔧 {user_data['weaponLevel']} 🤖 {user_data['tapBotLevel']}\n"
                            f"Boss 👾 {user_data['currentBoss']['level']} 💘 {user_data['currentBoss']['currentHealth']} - {user_data['currentBoss']['maxHealth']}\n"
                            f"Free 🚀 {user_data['freeBoosts']['currentTurboAmount']}\n"
                        )
                        print(output, end="", flush=True)

                        current_health = activate_booster(index, headers)

                        tap_attempts = 0  # Count the number of taps
                        last_health = current_health  # Store last health to check if it changes

                        while current_health is not None and current_health > 0:  # Continue while the boss is alive
                            tap_payload = {
                                "operationName": "MutationGameProcessTapsBatch",
                                "variables": {
                                    "payload": {
                                        "nonce": generate_random_nonce(),
                                        "tapsCount": 500000  # Adjust the tap count as needed
                                    }
                                },
                                "query": MUTATION_GAME_PROCESS_TAPS_BATCH
                            }

                            tap_result = submit_taps(index, tap_payload)
                            if tap_result is not None:
                                tap_data = tap_result['data']['telegramGameProcessTapsBatch']
                                current_health = tap_data['currentBoss']['currentHealth']
                                print(f"\rTapped ✅ Boss Health: {current_health}/{tap_data['currentBoss']['maxHealth']}")

                                # Check if boss health has not changed
                                if current_health == last_health:
                                    tap_attempts += 1
                                else:
                                    tap_attempts = 0  # Reset count if health changes

                                last_health = current_health  # Update the last health

                                # If taps are repeated and boss health is not changing, restart
                                if tap_attempts >= 5:  # Adjust the number as needed
                                    print("\n🎯 Boss health is not decreasing. Restarting...")
                                    break  # Break the loop to restart the script

                            else:
                                print(f"🎯 Failed to tap, trying again...")

                        if current_health <= 0:  # Check if the boss is defeated
                            print("\nBoss defeated, setting next boss...", flush=True)
                            set_next_boss(index, headers)
                            time.sleep(3)  # Wait 10 seconds before continuing to the next boss
                    else:
                        break  # Exit the while loop if no valid stats are returned

        except Exception as e:
            print(f"🎯 An error occurred: {e}. Restarting from account list...")

# Run the main() function
main()
