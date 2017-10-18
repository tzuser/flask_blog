from webapp import create_app

if __name__ == '__main__':
    app=create_app('webapp.config.DevConfig')
    app.run(threaded=True)