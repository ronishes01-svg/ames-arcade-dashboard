#!/bin/bash
# הרצת הדאשבורד — פותח חלון כרום חדש על הכתובת
cd "$(dirname "$0")"
PORT=8512
lsof -ti:$PORT | xargs kill -9 2>/dev/null
.venv/bin/streamlit run app.py --server.port $PORT --server.headless true &
until curl -s -o /dev/null http://localhost:$PORT; do sleep 1; done
sleep 4
open -na "Google Chrome" --args --new-window "http://localhost:$PORT"
wait
