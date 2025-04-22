from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import logging
import json
from DecriptionAlgorithm import string_to_values
import uvicorn
import base64

# Initialize FastAPI app
app = FastAPI()

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["api_database"]
collection = db["string_data"]

# Paths to the RSA keys change into your own path make sure to do double slashes so they become readable to the script 
PRIVATE_KEY_PATH = "C:\\Users\\Codeline User\\Desktop\\Haroon_Folder\\keys\\private.pem"
PUBLIC_KEY_PATH = "C:\\Users\\Codeline User\\Desktop\\Haroon_Folder\\keys\\public.pem"

# Load RSA private key if your key requires a password insert it instead of none
with open(PRIVATE_KEY_PATH, "rb") as private_key_file:
    private_key = serialization.load_pem_private_key(
        private_key_file.read(),
        password=None
    )

# Load RSA public key
with open(PUBLIC_KEY_PATH, "rb") as public_key_file:
    public_key = serialization.load_pem_public_key(public_key_file.read())

# ...existing code...

# Helper functions for encryption and decryption
def encrypt_data(data: str) -> bytes:
    return public_key.encrypt(
        data.encode(),
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    )

def decrypt_data(encrypted_data: bytes) -> str:
    return private_key.decrypt(
        encrypted_data,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    ).decode()

# Debugging log setup
DEBUG_LOG_FILE_PATH = "debug.log"
if not DEBUG_LOG_FILE_PATH:
    # Create the debug log file if it doesn't exist
    with open(DEBUG_LOG_FILE_PATH, "w") as f:
        f.write("")

logging.basicConfig(
    filename=DEBUG_LOG_FILE_PATH,
    level=logging.DEBUG,  # Set logging level to DEBUG
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Pydantic model for input
class StringInput(BaseModel):
    input_string: str

# Helper functions for encryption and decryption
def encrypt_data(data: str) -> bytes:
    return public_key.encrypt(
        data.encode(),
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    )

def decrypt_data(encrypted_data: bytes) -> str:
    return private_key.decrypt(
        encrypted_data,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    ).decode()

# Add a GET endpoint to process input via query parameters
@app.get("/process/")
async def process_string_via_get(convert_measurements: str):
    try:
        # Process the input string
        output = string_to_values(convert_measurements)

        # Serialize the output to a JSON string
        output_json = json.dumps(output)

        # Encrypt input and output with Base64 encoding
        encrypted_input = base64.b64encode(encrypt_data(convert_measurements)).decode('utf-8')
        encrypted_output = base64.b64encode(encrypt_data(output_json)).decode('utf-8')

        # Store in MongoDB
        collection.insert_one({"input": encrypted_input, "output": encrypted_output})

        # Log the request
        logging.debug(f"Processed input: {convert_measurements}, Output: {output}")

        return {"message": "Data processed successfully", "output": output}
    except Exception as e:
        logging.error(f"Error processing input: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# GET endpoint to retrieve and decrypt data
@app.get("/retrieve/")
async def retrieve_data():
    try:
        # Retrieve all data from MongoDB
        records = collection.find()
        decrypted_data = []

        for record in records:
            # Decode Base64 before decryption
            decrypted_input = decrypt_data(base64.b64decode(record["input"]))
            decrypted_output = json.loads(decrypt_data(base64.b64decode(record["output"])))  # Deserialize JSON string
            decrypted_data.append({"input": decrypted_input, "output": decrypted_output})

        # Log the retrieval
        logging.debug("Retrieved data from database")

        return {"data": decrypted_data}
    except Exception as e:
        logging.error(f"Error retrieving data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# DELETE endpoint to clear the database
@app.delete("/clear/")
async def clear_database():
    try:
        # Delete all documents in the collection
        result = collection.delete_many({})
        logging.debug(f"Cleared database. Deleted {result.deleted_count} documents.")
        return {"message": f"Cleared database. Deleted {result.deleted_count} documents."}
    except Exception as e:
        logging.error(f"Error clearing database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# Run the API locally on port 8888
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)