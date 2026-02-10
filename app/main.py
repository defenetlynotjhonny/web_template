from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>FastAPI Page</title>
        </head>
        <body>
            <h1>Hello from FastAPI 🚀</h1>
            <p>This is a basic FastAPI page.</p>
        </body>
    </html>
    """
