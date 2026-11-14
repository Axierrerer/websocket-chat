import asyncio
import sys

from entrypoints.uvicorn_run import main as uvicorn_main

if __name__ == "__main__":
    if "--uvicorn" in sys.argv:
        asyncio.run(uvicorn_main())
