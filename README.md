# Let AI organize your Gmail

## What you need:
- Python 3.10 or newer, then install the dependencies: `pip install -r requirements.txt`
- rename the .env.example file to .env and fill in your openai api key and your email
- modify the constants file days_back to however many days back you want to search for emails
- enable the gmail API (important): steps followed here -> [GMail API](https://developers.google.com/gmail/api/quickstart/python#authorize_credentials_for_a_desktop_application)
- create a credentials folder, and then when you get your json file from Google, rename it to 'credentials.json' and add it to this folder
- when done, run `python main.py` from this folder. The first run opens a browser for Google sign-in and saves `credentials/token.json`

## In future, will think about automating this with CrewAI, but it doesn't seem necessary atm.
