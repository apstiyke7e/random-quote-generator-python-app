# Random Quote Generator

A small Flask app that shows a different original quote each time you refresh the page.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser. Use `python -m venv .venv` and
`.venv\Scripts\activate.bat` if you use Command Prompt instead of PowerShell.

For deployment, set a stable, secret `SECRET_KEY` environment variable. Set
`FLASK_DEBUG=1` to enable Flask's development debugger when running locally.
