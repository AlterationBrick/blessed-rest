from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/tilt/up")
def tilt_up():
    print("tilt up")
    return "tilt manual"
    
@app.route("/tilt/down")
def tilt_down():
    print("tilt down")
    return "tilt manual"
    
@app.route("/tilt/stop")
def tilt_stop():
    print("tilt stop")
    return "tilt manual"
    
@app.route("/tilt/auto")
def tilt_auto():
    print("tilt auto")
    return "tilt auto"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)