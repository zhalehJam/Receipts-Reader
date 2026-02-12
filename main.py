
# main.py
"""
Receipt Processing Application
Main entry point
"""
from gui.main_window import MainWindow
from webapp import main as webapp_main
import uvicorn
def main():
    """Main application entry point"""
    try:
        # Uncomment the following lines if you want to run the GUI application
        # app = MainWindow()
        # app.run()

        # If webapp_main is a FastAPI/Flask app, use an ASGI/WSGI server to run it
       
        uvicorn.run(app=webapp_main.app, host="localhost", port=8000)
    except Exception as e:
        print(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()