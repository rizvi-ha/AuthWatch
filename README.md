# AuthWatch

AuthWatch aims to be an open-source web-based dashboard that ingests standard login logs and displays security-relevant metrics through interactive Plotly graphs. 
This project targets users who may not have the resources to invest in full-scale enterprise solutions such as Okta but still require robust login monitoring.

## Setup instructions (for dev environment, deploying will require more steps)

1. Create a .env file with your Supabase credentials
   
```
SUPABASE_URL=www.something.com
SUPABASE_KEY=2ddd3r2r
```

2. Setup python virtual environment

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Run dev server

```
python app.py
```

4. Everytime you restart terminal
   
```
source venv/bin/activate
```
