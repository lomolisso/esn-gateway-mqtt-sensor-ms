import uvicorn
from app.publisher import app

def run_publisher_process(publisher_host, publisher_port):
    uvicorn.run(app=app, host=publisher_host, port=publisher_port)
