from flask import Flask, request, jsonify, redirect, url_for
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from datetime import datetime

app = Flask(__name__)

# This should be False in production
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Gets an authorized Gmail API service instance."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = Flow.from_client_secrets_file(
                'credentials.json',
                scopes=SCOPES,
                redirect_uri='http://localhost:5000/oauth2callback'
            )
            auth_url, _ = flow.authorization_url(prompt='consent')
            return None, auth_url
            
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    service = build('gmail', 'v1', credentials=creds)
    return service, None

@app.route('/')
def index():
    """Enhanced home page with search form"""
    return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Gmail Search</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .search-container {
                    margin: 20px 0;
                }
                input[type="text"] {
                    width: 70%;
                    padding: 10px;
                    font-size: 16px;
                }
                input[type="submit"] {
                    padding: 10px 20px;
                    font-size: 16px;
                    background-color: #4285f4;
                    color: white;
                    border: none;
                    cursor: pointer;
                }
                #results {
                    margin-top: 20px;
                }
                .email-item {
                    border: 1px solid #ddd;
                    padding: 10px;
                    margin: 10px 0;
                    border-radius: 4px;
                }
                .email-subject {
                    color: #1a73e8;
                    font-weight: bold;
                }
                .email-from {
                    color: #666;
                    font-size: 0.9em;
                }
                .email-date {
                    color: #666;
                    font-size: 0.9em;
                }
                .help-text {
                    margin: 20px 0;
                    padding: 10px;
                    background-color: #f8f9fa;
                    border-radius: 4px;
                }
            </style>
            <script>
                function searchEmails() {
                    const query = document.getElementById('search-input').value;
                    fetch(`/search?query=${encodeURIComponent(query)}`)
                        .then(response => response.json())
                        .then(data => {
                            const resultsDiv = document.getElementById('results');
                            resultsDiv.innerHTML = '';
                            
                            data.forEach(email => {
                                const emailDiv = document.createElement('div');
                                emailDiv.className = 'email-item';
                                emailDiv.innerHTML = `
                                    <div class="email-subject">
                                        <a href="${email.url}" target="_blank">${email.subject}</a>
                                    </div>
                                    <div class="email-from">From: ${email.from}</div>
                                    <div class="email-date">Date: ${email.date}</div>
                                `;
                                resultsDiv.appendChild(emailDiv);
                            });
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            document.getElementById('results').innerHTML = 
                                '<div style="color: red;">Error fetching results</div>';
                        });
                    return false;
                }
            </script>
        </head>
        <body>
            <h1>Gmail Search</h1>
            
            <div class="help-text">
                <h3>Search Tips:</h3>
                <ul>
                    <li>from:sender - Find messages from a specific sender</li>
                    <li>to:recipient - Find messages to a specific recipient</li>
                    <li>subject:topic - Search in subject lines only</li>
                    <li>has:attachment - Find emails with attachments</li>
                    <li>after:2024/01/01 - Find emails after a specific date</li>
                </ul>
            </div>

            <div class="search-container">
                <form onsubmit="return searchEmails()">
                    <input type="text" id="search-input" placeholder="Search emails... (e.g., from:someone@example.com subject:meeting)">
                    <input type="submit" value="Search">
                </form>
            </div>

            <div id="results"></div>
        </body>
        </html>
    """

@app.route('/search')
def search_emails():
    """Search Gmail and return results"""
    service, auth_url = get_gmail_service()
    
    if not service:
        return redirect(auth_url)
        
    try:
        query = request.args.get('query', '')
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=20  # Increased from 10 to 20
        ).execute()

        messages = []
        if 'messages' in results:
            for msg in results['messages']:
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['subject', 'from', 'date']
                ).execute()
                
                headers = message['payload']['headers']
                subject = next(
                    (h['value'] for h in headers if h['name'].lower() == 'subject'),
                    '(no subject)'
                )
                sender = next(
                    (h['value'] for h in headers if h['name'].lower() == 'from'),
                    '(no sender)'
                )
                date_str = next(
                    (h['value'] for h in headers if h['name'].lower() == 'date'),
                    ''
                )
                try:
                    # Parse and format the date
                    date_obj = datetime.strptime(date_str.split(' (')[0].strip(), '%a, %d %b %Y %H:%M:%S %z')
                    formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted_date = date_str
                
                messages.append({
                    'id': msg['id'],
                    'subject': subject,
                    'from': sender,
                    'date': formatted_date,
                    'url': f"https://mail.google.com/mail/u/0/#inbox/{msg['id']}"
                })
                
        return jsonify(messages)

    except HttpError as error:
        return jsonify({'error': str(error)}), 500

# OAuth callback route remains the same
@app.route('/oauth2callback')
def oauth2callback():
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        redirect_uri='http://localhost:5000/oauth2callback'
    )
    
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    
    creds = flow.credentials
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)