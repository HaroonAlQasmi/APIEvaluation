# APIEvaluation

Make sure you have:

- Python 3.8 or later.
- MongoDB installed and running on `localhost:27017`.
- Required Python packages: `fastapi`, `uvicorn`, `pymongo`, `cryptography`.
- `DecriptionAlgorithm.py` file in the same directory as the server script.
- Write permissions for logging (`api_history.log`).
- Make sure you give permissions to the port to be used (here it is port `8888`).
- Change the path of the RSA keys in the code to your own keys' path.
- **Make sure to delete `__pycache__` and `debug.log`. They are there as a proof of concept and may cause errors.**

Run the `APIEv_Server_app.py` file and use the following URL format to test strings:

```
http://(Your IP Address):8888/process/?convert_measurements=(the string you wish to test)
```

To view the history database, use the following URL format:

```
http://(Your IP Address):8888/retrieve/
```

If you ever wish to clear the database, use the following command in CMD:

```
curl -X DELETE "http://127.0.0.1:8888/clear/"
```