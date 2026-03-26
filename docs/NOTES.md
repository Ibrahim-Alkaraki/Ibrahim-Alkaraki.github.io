# Resume Project - Notes

## How to Run
```bash
# Terminal 1 - Start the backend API server
python3 server.py

# Terminal 2 - Start the web server
python3 http_server.py

# Then open in browser:
# http://localhost:8000/RESUME.html
```

## Project Structure
```
ResumeRepo/
├── RESUME.html              # Main interactive resume website
├── fun_system_event.html    # Bonus page (linked from "PRESS ME" button)
├── server.py                # Backend API - runs Python demos from browser (port 5000)
├── http_server.py           # Serves RESUME.html to browser (port 8000)
├── scripts/                 # Interactive demo scripts
│   ├── password_manager_enhanced.py
│   ├── network_device_manager_enhanced.py
│   ├── file_manager_enhanced.py
│   └── log_parsing_analysis.py
├── docs/                    # Documentation
│   ├── NOTES.md
│   └── LINUX_DEPLOYMENT.md
└── deploy/                  # Deployment automation
    └── setup_resume.sh
```

## Requirements
- **Python 3.6+** (only built-in modules for server/file manager/network manager)
- **cryptography** module (only needed for password manager): `pip3 install cryptography`

## Important Notes
- All 3 demo scripts store data **in memory only** - nothing touches your real filesystem
- Data resets each time a script is started from the browser
- `server.py` runs on port **5000**, `http_server.py` runs on port **8000**
- If ports are in use, kill existing processes: `lsof -ti:5000 | xargs kill` / `lsof -ti:8000 | xargs kill`

## Backup
Deleted files are saved at `~/Desktop/DELETEDRESUMEFILES/` in case you need them back.
