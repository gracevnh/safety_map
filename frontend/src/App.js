import React, { useState } from 'react';
import axios from 'axios';
import MapComponent from './components/MapComponent';
import './App.css';

function App() {
  const [start, setStart] = useState(null);
  const [end, setEnd] = useState(null);
  const [message, setMessage] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/route', { start, end });
      setMessage(response.data.message);
    } catch (error) {
      setMessage('Error: ' + error.response.data.error);
    }
  };

  return (
    <div className="App">
      <h1>Walk Safe</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Start Point:</label>
          <MapComponent setLocation={setStart} />
        </div>
        <div className="form-group">
          <label>End Point:</label>
          <MapComponent setLocation={setEnd} />
        </div>
        <button type="submit">Create Route</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}

export default App;
