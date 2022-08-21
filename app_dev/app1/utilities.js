// Helper code to make a get request. Default parameter of empty JSON Object for params.
// Returns a Promise to a JSON Object.
export function get(endpoint, params = {}) {
    const fullPath = endpoint + "?" + formatParams(params);
    return fetch(fullPath)
      .then(convertToJSON)
      .catch((error) => {
        // give a useful error message
        throw `GET request to ${fullPath} failed with error:\n${error}`;
      });
  }
  
  // Helper code to make a post request. Default parameter of empty JSON Object for params.
  // Returns a Promise to a JSON Object.
  export function post(endpoint, params = {}) {
    return fetch(endpoint, {
      method: "post",
      headers: { "Content-type": "application/json" },
      body: JSON.stringify(params),
    })
      .then(convertToJSON) // convert result to JSON object
      .catch((error) => {
        // give a useful error message
        throw `POST request to ${endpoint} failed with error:\n${error}`;
      });
  }
  