function input_string() {
    let user_string = document.getElementById("user_string").value;
    fetch(`http://127.0.0.1:8888/process/?convert_measurements=${user_string}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const container = document.getElementById('result_div');
            container.innerHTML = ''; // Clear previous results
            container.style = 'background-color: greenyellow; border-radius: 10px; padding: 10px; display: inline-block;';
            container.innerHTML = `<p>The strings value: [${data.output.join(', ')}]</p>`;
        })
        .catch(error => {
            console.error("Error fetching data:", error);
        });
}

function getHistory() {
    fetch('http://127.0.0.1:8888/retrieve/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const container = document.getElementById('history_div');
            container.innerHTML = ''; // Clear previous history
            data.data.forEach(post => {
                const postDiv = document.createElement('div');
                postDiv.innerHTML = `
                    <h3>The User's input string: ${post.input}</h3>
                    <p>The string's value: [${post.output.join(', ')}]</p>
                `;
                container.appendChild(postDiv);
            });
            container.style = "background-color: lightgreen; border-radius: 10px; padding: 10px; display: inline-block;";
        })
        .catch(error => {
            console.error("Error fetching history:", error);
        });
}

function clearDiv() {
    let divToClear = document.getElementById("history_div");
    divToClear.innerHTML = ``;
}