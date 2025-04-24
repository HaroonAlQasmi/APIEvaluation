# APIEvaluation

## Prerequisites

Ensure the following requirements are met before running the application:

- **Python Version**: Python 3.8 or later.
- **MongoDB**: Installed and running on `localhost:27017`.
- **Python Packages**: Install the required packages: `fastapi`, `uvicorn`, `pymongo`, `cryptography`.
- **Script Dependency**: Place the `DecriptionAlgorithm.py` file in the same directory as the server script.
- **Logging Permissions**: Ensure write permissions for logging.
- **Port Permissions**: Grant permissions for the port to be used (default is port `8888`).
- **RSA Keys**: Update the path of the RSA keys in the code to match your own keys' path.
- **Cleanup**: Delete the `__pycache__` folder and `debug.log` file. These are for proof of concept and may cause errors.

---

## Running the Server

1. Run the `APIEv_Server_app.py` file.
2. Use the following URL format to test strings:

    ```
    http://(Your IP Address):8888/process/?convert_measurements=(the string you wish to test)
    ```

3. To view the history database, use this URL format:

    ```
    http://(Your IP Address):8888/retrieve/
    ```

4. To clear the database, execute the following command in CMD:

    ```
    curl -X DELETE "http://127.0.0.1:8888/clear/"
    ```

---

## Notes

- The data is visible while the server is running. You can view it using MongoDB Compass.
- To access the database, connect to `mongodb://localhost:27017/`.
- The string data will appear in a database named `api_database`.

---

## Running the Frontend

1. Ensure the server application is running and the prerequisites are met.
2. Open the `.html` file in your browser.
3. Enter the desired string in the input field.
4. Press the **Submit** button to display the converted value below.
5. Repeat steps 3 and 4 with a new string to replace the old value.
6. To view the history of strings, press the **Show History** button.
7. To clear the history, press the **Clear** button on the page.