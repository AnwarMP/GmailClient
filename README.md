# Gmail Flask Application

This is a Flask application that integrates with Gmail API to provide email searching capabilities.

## Requirements

See `requirements.txt` below for Python dependencies:

```txt
flask==3.0.0
google-auth-oauthlib==1.2.0
google-auth==2.27.0
google-api-python-client==2.116.0
```

## Setup Instructions

1. **Create and activate conda environment**
   ```bash
   # Create new conda environment with Python 3.10
   conda create -n gmail-flask python=3.10
   
   # Activate the environment
   conda activate gmail-flask
   ```

2. **Install requirements**
   ```bash
   # Install requirements using pip
   pip install -r requirements.txt
   ```

3. **Set up Google Cloud Project**
   - Go to Google Cloud Console
   - Create a new project
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download the credentials and save as `credentials.json` in the project directory

4. **Run the application**
   ```bash
   # Set environment variable for development
   export OAUTHLIB_INSECURE_TRANSPORT=1  # For development only
   
   # Run Flask app
   flask run
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - You will be prompted to authenticate with your Google account
   - After authentication, you can use the search functionality

## Security Notes
- The `OAUTHLIB_INSECURE_TRANSPORT` environment variable should only be set in development
- In production, always use HTTPS
- Keep your `credentials.json` and `token.json` files secure and never commit them to version control

## Files
- `app.py`: Main Flask application
- `requirements.txt`: Python dependencies
- `credentials.json`: Google OAuth credentials (not included - you need to create this)
- `token.json`: Generated after authentication (will be created automatically)


I followed this tutorial on setting up Gmail on Google Cloud: [Tutorial](https://www.youtube.com/watch?v=7E3NNxeXiys&embeds_referring_euri=https%3A%2F%2Fwww.google.com%2Fsearch%3Fsca_esv%3Debc5f503c41e575a%26sxsrf%3DADLYWIIQp87xtIlBzCiHJFnI6Ivgj5Na_A%3A1730593913321%26q%3Dgmail%2Bapi%26tbm%3Dvi&source_ve_path=Mjg2NjY) 
