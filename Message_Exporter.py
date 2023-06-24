import requests

SETTINGS_FILE = 'settings.txt'
MESSAGES_PER_REQUEST = 100

def get_user_token():
    token = input("Enter your Discord user token: ")
    return token.strip()

def get_channel_id():
    channel_id = input("Enter the channel ID: ")
    return channel_id.strip()

def save_token(token):
    with open(SETTINGS_FILE, 'w') as file:
        file.write(token)

def load_token():
    with open(SETTINGS_FILE, 'r') as file:
        return file.read().strip()

def test_token(token):
    headers = {
        'Authorization': token
    }

    url = 'https://discord.com/api/v10/users/@me'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return True

    return False

def export_messages(token, channel_id):
    headers = {
        'Authorization': token
    }

    messages = []
    before = None

    print("Exporting messages...")
    print("This may take a while depending on the number of messages.")

    while True:
        url = f'https://discord.com/api/v10/channels/{channel_id}/messages?limit={MESSAGES_PER_REQUEST}'
        if before:
            url += f'&before={before}'

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print('Failed to fetch messages. Please check your token and channel ID.')
            return

        batch = response.json()
        messages.extend(batch)

        if len(batch) < MESSAGES_PER_REQUEST:
            break

        before = batch[-1]['id']

    messages.reverse()

    message_content = []
    for message in messages:
        content = message['content']
        author = message['author']['username']
        timestamp = message['timestamp']

        formatted_timestamp = timestamp.split('T')[0] + ' ' + timestamp.split('T')[1][:8]

        if 'attachments' in message:
            attachments = message['attachments']
            for attachment in attachments:
                attachment_url = attachment['url']
                content += f' ({attachment_url})'

        formatted_message = f'{formatted_timestamp} - {author}: {content}'
        message_content.append(formatted_message)

    with open('exported_messages.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(message_content))

    print('Messages exported successfully.')

def main():
    token = ''
    use_stored_token = False

    try:
        token = load_token()
        option = input("Do you want to use the previously used token? (y/n): ")
        if option.lower() == 'y':
            use_stored_token = True
    except FileNotFoundError:
        pass

    if not use_stored_token:
        token = get_user_token()

    if test_token(token):
        save_token(token)
        channel_id = get_channel_id()
        export_messages(token, channel_id)
    else:
        print('Invalid token. Please provide a valid Discord user token.')

if __name__ == '__main__':
    main()
