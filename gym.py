from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory data for demonstration
members = []
classes = []

@app.route('/')
def home():
    return jsonify({"message": "Welcome to ACEest Fitness & Gym API"})

@app.route('/members', methods=['GET', 'POST'])
def manage_members():
    if request.method == 'GET':
        return jsonify(members)
    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({"error": "Name is required"}), 400
        member = {"id": len(members) + 1, "name": data['name'], "email": data.get('email', '')}
        members.append(member)
        return jsonify(member), 201

@app.route('/classes', methods=['GET', 'POST'])
def manage_classes():
    if request.method == 'GET':
        return jsonify(classes)
    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'name' not in data or 'instructor' not in data:
            return jsonify({"error": "Name and instructor are required"}), 400
        gym_class = {"id": len(classes) + 1, "name": data['name'], "instructor": data['instructor'], "capacity": data.get('capacity', 20)}
        classes.append(gym_class)
        return jsonify(gym_class), 201

if __name__ == '__main__':
    app.run(debug=True)