from webapp import create_reptile

if __name__ == '__main__':
    app=create_reptile('webapp.config.DevConfig')
    app.run(host='0.0.0.0',port=5000,threaded=True)