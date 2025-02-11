from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def home():
    return {'message': 'Welcome to Render API!'}

if __name__ == "__main__":
    app.run()