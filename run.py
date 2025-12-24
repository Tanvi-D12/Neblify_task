#!/usr/bin/env python
"""Simple script to run the Deel AI Challenge API."""

import sys
import subprocess

if __name__ == "__main__":
    try:
        # Run the FastAPI application with uvicorn
        subprocess.run(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--reload",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
            ],
            cwd=".",
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
