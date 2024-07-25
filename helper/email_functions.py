import os
from typing import Any, Dict, List
from dotenv import load_dotenv
from openai import OpenAI

from constants import constants

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def is_important(msg, subject):
    keywords = ["urgent", "important", "action required"]
    for keyword in keywords:
        if keyword in subject.lower() or keyword in msg:
            return True
    return False


def create_label(service, user_id, label_name):
    label = {
        'name': label_name,
        'messageListVisibility': 'show',
        'labelListVisibility': 'labelShow'
    }
    try:
        created_label = service.users().labels().create(userId=user_id, body=label).execute()
        print(f'Label created: {created_label["id"]}')
        return created_label['id']
    except Exception as e:
        print(f'An error occurred: {e}')
        return None


def get_label_id(service, user_id, label_name):
    try:
        labels = service.users().labels().list(userId=user_id).execute()
        for label in labels['labels']:
            found_label = str(label['name'])
            if found_label.lower() == label_name.lower():
                return label['id']
        return create_label(service, user_id, label_name)
    except Exception as e:
        print(f'An error occurred: {e}')
        return None


def apply_label(service, user_id, msg_id, label_id):
    try:
        # labels_to_remove = message.get('labelIds', [])
        labels_to_remove = 'INBOX'
        msg_labels = {'removeLabelIds': [labels_to_remove], 'addLabelIds': [label_id]}
        message = service.users().messages().modify(userId=user_id, id=msg_id, body=msg_labels).execute()
        print(f'Label applied to message: {message["id"]}')
    except Exception as e:
        print(f'An error occurred: {e}')


def check_labels(service, response_objects: List[Dict[str, Any]]):
    list_of_labels = constants.list_of_labels

    for object in response_objects:
        # check if the email is important
        if is_important(object.get('body'), object.get('subject')):
            # apply the "Important" label to the email
            label_id = get_label_id(service, 'me', 'Important')
            if label_id:
                apply_label(service, 'me', object.get('id'), label_id)
        else:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a gmail sorting expert."
                    },
                    {
                        "role": "user",
                        "content": f"""Tell me which label the body of this email {object.get('body')}
                                    from this list: {list_of_labels}.  Only return the label.  If you don't know
                                    how to categorize the label, then name the label Miscellaneous."""
                    }
                ]
            )

            ai_label = completion.choices[0].message.content

            label_id = get_label_id(service, 'me', ai_label)
            if label_id:
                apply_label(service, 'me', object.get('id'), label_id)


def clean_email_body(body: str) -> str:
    """Clean email body."""
    try:
        from bs4 import BeautifulSoup

        try:
            soup = BeautifulSoup(str(body), "html.parser")
            body = soup.get_text()
            return str(body)
        except Exception as e:
            print(e)
            return str(body)
    except ImportError:
        print("BeautifulSoup not installed. Skipping cleaning.")
        return str(body)
