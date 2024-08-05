from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/greet/<name>')
def greet(name):
    return f"Hello, {name}!"

@app.route('/json')
def json_example():
    data = {
        "message": "This is a JSON response",
        "status": "success"
    }
    return jsonify(data)

@app.route('/post_example', methods=['POST'])
def post_example():
    data = request.json
    return jsonify({
        "received_data": data
    })

if __name__ == '__main__':
    app.run(debug=True)
