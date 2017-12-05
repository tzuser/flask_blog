from webapp import create_app

if __name__ == '__main__':
    app=create_app('webapp.config.DevConfig')
    app.run(host='0.0.0.0',port=5100,threaded=True)