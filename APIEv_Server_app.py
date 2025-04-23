from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import logging
import json
from DecriptionAlgorithm import string_to_values
import uvicorn
import base64
import atexit
import os

# Initialize FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["api_database"]
collection = db["string_data"]

# Paths to the RSA keys
PRIVATE_KEY_PATH = "C:\\Users\\Codeline User\\Desktop\\Haroon_Folder\\keys\\private.pem"
PUBLIC_KEY_PATH = "C:\\Users\\Codeline User\\Desktop\\Haroon_Folder\\keys\\public.pem"

# Path to the DecriptionAlgorithm file
DECRIPTION_ALGORITHM_PATH = "C:\\Users\\Codeline User\\Desktop\\Haroon_Folder\\DecriptionAlgorithm.cpython"

# Load RSA private key
with open(PRIVATE_KEY_PATH, "rb") as private_key_file:
    private_key = serialization.load_pem_private_key(
        private_key_file.read(),
        password=None
    )

# Load RSA public key
with open(PUBLIC_KEY_PATH, "rb") as public_key_file:
    public_key = serialization.load_pem_public_key(public_key_file.read())

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
logging.basicConfig(
    filename=DEBUG_LOG_FILE_PATH,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Pydantic model for input
class StringInput(BaseModel):
    input_string: str

# Encrypt all data in the database
def encrypt_database():
    try:
        records = collection.find()
        for record in records:
            if not record.get("encrypted", False):  # Skip already encrypted records
                # Convert non-string data to JSON strings
                input_data = record["input"]
                output_data = record["output"]

                if isinstance(input_data, list):
                    input_data = json.dumps(input_data)
                if isinstance(output_data, list):
                    output_data = json.dumps(output_data)

                encrypted_input = base64.b64encode(encrypt_data(input_data)).decode('utf-8')
                encrypted_output = base64.b64encode(encrypt_data(json.dumps(output_data))).decode('utf-8')
                collection.update_one(
                    {"_id": record["_id"]},
                    {"$set": {"input": encrypted_input, "output": encrypted_output, "encrypted": True}}
                )
        logging.debug("Database encrypted successfully on server shutdown.")
    except Exception as e:
        logging.error(f"Error encrypting database: {str(e)}")

# Decrypt all data in the database
def decrypt_database():
    try:
        records = collection.find()
        for record in records:
            if record.get("encrypted", False):  # Only decrypt encrypted records
                decrypted_input = decrypt_data(base64.b64decode(record["input"]))
                decrypted_output = json.loads(decrypt_data(base64.b64decode(record["output"])))

                # Convert JSON strings back to lists if necessary
                try:
                    decrypted_input = json.loads(decrypted_input)
                except json.JSONDecodeError:
                    pass  # Keep as string if not JSON

                try:
                    decrypted_output = json.loads(decrypted_output)
                except json.JSONDecodeError:
                    pass  # Keep as string if not JSON

                collection.update_one(
                    {"_id": record["_id"]},
                    {"$set": {"input": decrypted_input, "output": decrypted_output, "encrypted": False}}
                )
        logging.debug("Database decrypted successfully on server startup.")
    except Exception as e:
        logging.error(f"Error decrypting database: {str(e)}")

# Encrypt the DecriptionAlgorithm file
def encrypt_file(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                file_data = file.read()
            encrypted_data = encrypt_data(file_data.decode())
            with open(file_path, "wb") as file:
                file.write(encrypted_data)
            logging.debug(f"File {file_path} encrypted successfully.")
    except Exception as e:
        logging.error(f"Error encrypting file {file_path}: {str(e)}")

# Decrypt the DecriptionAlgorithm file
def decrypt_file(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                encrypted_data = file.read()
            decrypted_data = decrypt_data(encrypted_data)
            with open(file_path, "w") as file:
                file.write(decrypted_data)
            logging.debug(f"File {file_path} decrypted successfully.")
    except Exception as e:
        logging.error(f"Error decrypting file {file_path}: {str(e)}")

# Decrypt database and file on server startup
decrypt_database()
decrypt_file(DECRIPTION_ALGORITHM_PATH)

# Encrypt database and file on server shutdown
atexit.register(encrypt_database)
atexit.register(lambda: encrypt_file(DECRIPTION_ALGORITHM_PATH))

# Add a GET endpoint to process input via query parameters
@app.get("/process/")
async def process_string_via_get(convert_measurements: str):
    try:
        # Process the input string
        output = string_to_values(convert_measurements)

        # Serialize the output to a JSON string
        output_json = json.dumps(output)

        # Store in MongoDB without encryption (encryption happens on shutdown)
        collection.insert_one({"input": convert_measurements, "output": output, "encrypted": False})

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
            # If data is encrypted, decrypt it
            if record.get("encrypted", False):
                decrypted_input = decrypt_data(base64.b64decode(record["input"]))
                decrypted_output = json.loads(decrypt_data(base64.b64decode(record["output"])))

                # Convert JSON strings back to lists if necessary
                try:
                    decrypted_input = json.loads(decrypted_input)
                except json.JSONDecodeError:
                    pass  # Keep as string if not JSON

                try:
                    decrypted_output = json.loads(decrypted_output)
                except json.JSONDecodeError:
                    pass  # Keep as string if not JSON
            else:
                decrypted_input = record["input"]
                decrypted_output = record["output"]

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
    try:
        uvicorn.run(app, host="0.0.0.0", port=8888)
    except KeyboardInterrupt:
        logging.info("Server is shutting down...")