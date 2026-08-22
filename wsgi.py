from app import app
import os
from dotenv import load_dotenv

#Ruta absoluta de las variables de entorno
project_folder = '/home/zairduarte22/becas_app'
load_dotenv(os.path.join(project_folder, '.env'))

if __name__ == "__main__":
    app.run()