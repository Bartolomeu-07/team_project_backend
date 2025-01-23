from flask import Flask, jsonify

from data import upcoming_matches


app = Flask(__name__)

@app.route('/api/upcoming-matches', methods=['GET'])
def get_upcoming_matches():
    return jsonify(upcoming_matches)

if __name__ == '__main__':
    app.run(debug=True)