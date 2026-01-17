from flask import Flask
from qhawariy import create_app

app: Flask = create_app(test_config=None)
