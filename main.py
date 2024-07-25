import base64
import email
from datetime import datetime, timedelta
from email import message_from_bytes
from typing import Any, Dict, List

from googleapiclient.discovery import build

import helper.credentials as cred
import helper.email_functions as ef


def main() -> List[Dict[str, Any]]:
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    response_objects = []
    creds = cred.get_credentials()

    service = build('gmail', 'v1', credentials=creds)

    now = datetime.utcnow()
    yesterday = (now - timedelta(days=5)).strftime('%Y/%m/%d')

    query = f'in:inbox after:{yesterday}'

    results = service.users().messages().list(userId='me', q=query, maxResults=100).execute()
    messages = results.get('messages', [])

    if not messages:
        print('No messages found.')
    else:
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='raw').execute()
            msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
            email_msg = email.message_from_bytes(msg_str)
            mime_msg = message_from_bytes(msg_str)

            if email_msg.is_multipart():
                for part in email_msg.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get("Content-Disposition"))
                    if ctype == "text/plain" and "attachment" not in cdispo:
                        message_body = part.get_payload(decode=True).decode("utf-8")
                        break
            else:
                message_body = email_msg.get_payload(decode=True).decode("utf-8")

            body = ef.clean_email_body(message_body)

            response_objects.append(
                {
                    "id": message["id"],
                    "threadId": msg["threadId"],
                    "snippet": msg["snippet"],
                    "body": body,
                    "subject": mime_msg['subject'],
                }
            )

    ef.check_labels(service, response_objects)

    return response_objects


if __name__ == '__main__':
    response = main()
    print(response)
