import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [caption, setCaption] = useState('');
  const [audio, setAudio] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setCaption(response.data.caption);
      setAudio(response.data.audio);
    } catch (error) {
      console.error('Error uploading file', error);
    }
  };

  return (
    <div className="App">
      <h1>Voice Based Image Caption Generator</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} />
        <button type="submit">Upload and Generate Caption</button>
      </form>
      {caption && <p>Caption: {caption}</p>}
      {audio && <audio controls src={`http://localhost:5000/${audio}`}></audio>}
    </div>
  );
}

export default App;
