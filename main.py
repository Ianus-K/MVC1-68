import os
from controller.app_controller import AppController

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    app = AppController(project_root)
    app.run()