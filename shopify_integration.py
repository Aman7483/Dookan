# # shopify_integration.py
# import requests
# from flask import Flask, jsonify, request

# app = Flask(__name__)

# SHOPIFY_API_URL = "https://dookan-dev-plus.myshopify.com/admin/api/2023-07"
# ACCESS_TOKEN = "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"

# # ...

# # REST API endpoint to create a product
# @app.route("/api/shopify/products/rest/create", methods=["POST"])
# def create_shopify_product_rest():
#     data = request.get_json()
#     title = data.get("title")
#     body_html = data.get("body_html")
#     vendor = data.get("vendor")
#     product_type = data.get("product_type")

#     # Validate that required fields are present
#     if not title or not body_html or not vendor or not product_type:
#         return jsonify({"error": "Title, body_html, vendor, and product_type are required"}), 400

#     # Construct the REST API endpoint
#     url=f"https://dookan-dev-plus.myshopify.com/products.json"
    
#     # Build the payload for creating a product
#     payload = {
#         "product": {
#             "title": title,
#             "body_html": body_html,
#             "vendor": vendor,
#             "product_type": product_type,
#             "status": "draft",  # You can adjust the status as needed
#         }
#     }

#     # Set up headers
#     headers = {
#         "Content-Type": "application/json",
#         "X-Shopify-Access-Token": ACCESS_TOKEN,
#     }

#     # Make the POST request to create the product
#     response = requests.post(url, json=payload, headers=headers)

#     # Check the response status and return the result
#     if response.status_code == 201:
#         return jsonify(response.json()), 201
#     else:
#         return jsonify({"error": f"Failed to create product. Status code: {response.status_code}"}), response.status_code

# # ...

# if __name__ == "__main__":
#     app.run(debug=True)
