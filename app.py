"""Web app to generate SQL queries from user input using GPT-3"""
from app import create_app
import app.config as config

app = create_app()


# Run web app
if __name__ == '__main__':
    debug = config.DEBUG_MODE
    port = int(config.APP_PORT)
    app.run(debug=debug, port=port, host="0.0.0.0")
