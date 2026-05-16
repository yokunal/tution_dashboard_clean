# 📚 Student Profile Tracker

A Streamlit-based tutoring management dashboard that uses Google Sheets as a database backend.

## Features

- 📋 **Dashboard** - Overview of students, sessions, homework, and tests
- 👨‍🎓 **Student Management** - Add and manage student profiles
- 📝 **Teaching Logs** - Record tutoring sessions with topics and hours
- 📚 **Homework** - Track homework assignments and completion
- 📊 **Tests** - Record test scores and performance
- 🤖 **AI Report Generator** - Generate progress reports using MiniMax AI
- 📄 **PDF Export** - Download reports as PDF

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yokunal/tution_dashboard.git
cd tution_dashboard
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Credentials

#### Google Sheets Service Account
Create a service account in Google Cloud Console:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Sheets API
4. Create a service account and download the JSON key
5. Save the JSON file as `credentials/google_service_account.json`

#### Share Your Google Sheet
Create a Google Sheet named `Tutor_Assistant_Database` and share it with the service account email (found in the JSON file).

#### Streamlit Secrets
Create `.streamlit/secrets.toml`:
```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
client_email = "your-service-account@project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."

[minimax]
api_key = "your-minimax-api-key"
base_url = "https://api.minimax.chat"

[spreadsheet]
name = "Tutor_Assistant_Database"
```

### 4. Run the App
```bash
streamlit run app.py
```

## Deployment on Streamlit Cloud

1. Push this code to a GitHub repository
2. Go to [streamlit.io](https://streamlit.io) and sign in with GitHub
3. Create a new app and select this repository
4. Add your secrets in the Streamlit Cloud dashboard

## Project Structure

```
tution_dashboard/
├── app.py                 # Main Streamlit application
├── lib/
│   ├── database.py       # Google Sheets database manager
│   ├── ai_client.py      # MiniMax AI API client
│   └── pdf_generator.py  # PDF report generator
├── pages/                # Multi-page Streamlit pages
│   ├── Students.py
│   ├── Teaching_Logs.py
│   ├── Homework.py
│   ├── Tests.py
│   └── AI_Report_Generator.py
├── credentials/          # Google service account JSON (local only)
├── .streamlit/          # Streamlit secrets (local only)
├── requirements.txt     # Python dependencies
└── README.md
```

## Tech Stack

- **Frontend**: Streamlit
- **Database**: Google Sheets
- **AI**: MiniMax API (MiniMax-Text-01 model)
- **PDF**: fpdf2

## License

MIT License