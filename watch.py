import time
import subprocess
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CodeChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_app()
    
    def start_app(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
        self.process = subprocess.Popen([sys.executable, "src/backend/app.py"])
        
    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"Change detected in {event.src_path}")
            self.start_app()

if __name__ == "__main__":
    event_handler = CodeChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, "src", recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    observer.join()