from form_2D import create_app

app = create_app()
if __name__ == '__main__':
    # In case project run with docker, should not change port. But if we run it directly in host server, we can change it
    # In case port numner changed here, should change it in Dockerfile and gunicorn_config.py
    # debug mode should be changed to False in production
    app.run(host = '0.0.0.0', port = 5000, debug=True)
