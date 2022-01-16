from price import create_app
import localconfig

application = create_app(localconfig.DevConfig())

if __name__ == "__main__":
    application.run(host='0.0.0.0')
