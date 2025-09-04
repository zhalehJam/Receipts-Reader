
# main.py
"""
Receipt Processing Application
Main entry point
"""
from gui.main_window import MainWindow

def main():
    """Main application entry point"""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()