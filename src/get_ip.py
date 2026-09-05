import requests


def get_server_public_ip():
    try:
        public_ip = requests.get("https://api.ipify.org").text
        print(
            f"Your public ip is {public_ip}.\nRemember you have to open port if you want people to connect to your server\n\n\n"
        )

    except requests.RequestException as error:
        print(f"Error: {error}")
