# app.py
from flask import Flask, send_from_directory, request, jsonify
from flask_pymongo import PyMongo
import bcrypt
from flask_cors import CORS
import requests
import json
from bson import json_util

app = Flask(__name__)
CORS(app)

# Configure MongoDB
app.config['MONGO_URI'] = 'mongodb+srv://user0:9c7K5thwrjBKhrju@dookan.lfcjnkb.mongodb.net/dookan'
mongo = PyMongo(app)

# Create MongoDB collections
aman_auth_collection = mongo.db.aman_auth
aman_log_collection = mongo.db.aman_log

# Serve the React app on the root path
@app.route('/')
def serve_react_app():
    with open('aman/build/index.html', 'r') as file:
        return file.read()

# Serve static files from the React app
@app.route('/static/js/<path:filename>')
def serve_react_js(filename):
    return send_from_directory('aman/build/static/js', filename)

@app.route('/static/css/<path:filename>')
def serve_react_css(filename):
    return send_from_directory('aman/build/static/css', filename)

# Serve images
@app.route('/<path:filename>')
def serve_images(filename):
    return send_from_directory('aman/build', filename)

# Flask API routes go here
@app.route('/api/')
def api_home():
    return 'Flask API is running on /api/'

# Test MongoDB connection
@app.route('/test_mongo')
def test_mongo():
    db = mongo.db
    return 'Connected to MongoDB!'

# Registration endpoint
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check if the username already exists
    if aman_auth_collection.find_one({'username': username}):
        return jsonify({'error': 'Username already exists'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user_id = aman_auth_collection.insert_one({'username': username, 'password': hashed_password}).inserted_id
    return jsonify({'user_id': str(user_id)})

# Login endpoint
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = aman_auth_collection.find_one({'username': username})

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({'username': username})
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

# Shopify integration endpoints

#CREATE

@app.route("/api/shopify/products/rest/create", methods=["POST"])
def create_shopify_product_rest():
    data = request.get_json()
    title = data.get("title")
    body_html = data.get("body_html")
    vendor = data.get("vendor")
    product_type = data.get("product_type")

    # Validate that required fields are present
    if not title or not body_html or not vendor or not product_type:
        return jsonify({"error": "Title, body_html, vendor, and product_type are required"}), 400

    # Construct the REST API endpoint
    url = f"https://dookan-dev-plus.myshopify.com/admin/api/2023-07/products.json"

    # Build the payload for creating a product
    payload = {
        "product": {
            "title": title,
            "body_html": body_html,
            "vendor": vendor,
            "product_type": product_type,
            "status": "draft",
        }
    }

    # Set up headers
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": "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",  # Use your actual token here
    }

    # Make the POST request to create the product
    response = requests.post(url, json=payload, headers=headers)

    # Log the request and response to MongoDB
    log_entry = {
        "action": "create_product",
        "request_payload": payload,
        "response_status": response.status_code,
        "response_content": response.json() if response.status_code == 201 else response.text,
    }
    aman_log_collection.insert_one(log_entry)

    # Check the response status and return the result
    if response.status_code == 201:
        return jsonify(response.json()), 201
    else:
        return jsonify({"error": f"Failed to create product. Status code: {response.status_code}"}), response.status_code

#READ
# Shopify integration endpoint to read a product
@app.route("/api/shopify/products/rest/read/<product_id>", methods=["GET"])
def read_shopify_product_rest(product_id):
    # Construct the REST API endpoint
    url = f"https://dookan-dev-plus.myshopify.com/admin/api/2023-07/products/{product_id}.json"

    # Set up headers
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": "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",  # Use your actual token here
    }

    # Make the GET request to read the product
    response = requests.get(url, headers=headers)

    # Log the request and response to MongoDB
    log_entry = {
        "action": "read_product",
        "product_id": product_id,
        "response_status": response.status_code,
        "response_content": response.json() if response.status_code == 200 else response.text,
    }
    aman_log_collection.insert_one(log_entry)

    # Check the response status and return the result
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({"error": f"Failed to read product. Status code: {response.status_code}"}), response.status_code

#UPDATE
# Shopify integration endpoint to update a product
@app.route("/api/shopify/products/rest/update/<product_id>", methods=["PUT"])
def update_shopify_product_rest(product_id):
    data = request.get_json()

    # Construct the REST API endpoint
    url = f"https://dookan-dev-plus.myshopify.com/admin/api/2023-07/products/{product_id}.json"

    # Build the payload for updating a product
    payload = {
        "product": data,  # Assuming data contains the updated fields
    }

    # Set up headers
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": "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",  # Use your actual token here
    }

    # Make the PUT request to update the product
    response = requests.put(url, json=payload, headers=headers)

    # Log the request and response to MongoDB
    log_entry = {
        "action": "update_product",
        "product_id": product_id,
        "request_payload": payload,
        "response_status": response.status_code,
        "response_content": response.json() if response.status_code == 200 else response.text,
    }
    aman_log_collection.insert_one(log_entry)

    # Check the response status and return the result
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({"error": f"Failed to update product. Status code: {response.status_code}"}), response.status_code

#LIST
# Shopify integration endpoint to list products
@app.route("/api/shopify/products/rest/list", methods=["GET"])
def list_shopify_products_rest():
    # Construct the REST API endpoint
    url = "https://dookan-dev-plus.myshopify.com/admin/api/2023-07/products.json"

    # Set up headers
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": "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",  # Use your actual token here
    }

    # Make the GET request to list products
    response = requests.get(url, headers=headers)

    # Log the request and response to MongoDB
    log_entry = {
        "action": "list_products",
        "response_status": response.status_code,
        "response_content": response.json() if response.status_code == 200 else response.text,
    }
    aman_log_collection.insert_one(log_entry)

    # Check the response status and return the result
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({"error": f"Failed to list products. Status code: {response.status_code}"}), response.status_code

#DELETE
# Shopify integration endpoint to delete a product
@app.route("/api/shopify/products/rest/delete/<product_id>", methods=["DELETE"])
def delete_shopify_product_rest(product_id):
    # Construct the REST API endpoint
    url = f"https://dookan-dev-plus.myshopify.com/admin/api/2023-07/products/{product_id}.json"

    # Set up headers
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": "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",  # Use your actual token here
    }

    # Make the DELETE request to delete the product
    response = requests.delete(url, headers=headers)

    # Log the request and response to MongoDB
    log_entry = {
        "action": "delete_product",
        "product_id": product_id,
        "response_status": response.status_code,
        "response_content": response.json() if response.status_code == 200 else response.text,
    }
    aman_log_collection.insert_one(log_entry)

    # Check the response status and return the result
    if response.status_code == 200:
        return jsonify({"message": f"Product {product_id} deleted successfully"}), 200
    else:
        return jsonify({"error": f"Failed to delete product. Status code: {response.status_code}"}), response.status_code



# View logs endpoint
@app.route('/api/logs', methods=['GET'])
def view_logs():
    # Retrieve all log entries
    log_entries = aman_log_collection.find()

    # Extract 'action' field from each log entry
    actions = [entry['action'] for entry in log_entries]

    return jsonify(actions), 200


if __name__ == '__main__':
    app.run(debug=True)
