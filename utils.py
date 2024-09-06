import requests

def get_random_emoji():
    try:
        response = requests.get('https://emojihub.yurace.pro/api/random')
        if response.status_code == 200:
            emoji_data = response.json()
            return emoji_data['htmlCode'][0]  # Return the first HTML code
        else:
            print("Failed to fetch emoji, status code:", response.status_code)
            return '&#128512;'  # Default emoji if API call fails
    except Exception as e:
        print("Error fetching emoji:", str(e))
        return '&#128512;'  # Default emoji if any error occurs