/* root component that renders entire application
contains state data related to currently selected date, user preferences, and calendar data
*/

import React from 'react';
import './App.css';
import Columns from './Columns'; 

function App() {
  return (
    <div className="App">
      <Columns /> {/* Using the Columns component */}
    </div>
  );
}

export default App;
