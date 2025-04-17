#!/usr/bin/env python3
# This file is a simple entry point for Vercel
from vercel_app import app

# This is used by Vercel
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080))) 