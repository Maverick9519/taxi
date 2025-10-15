import React, { useState } from 'react';
import Passenger from './Passenger';
import Driver from './Driver';
function App() {
  const [role, setRole] = useState(null);
  if (!role) {
    return (
      <div style={{ padding: '20px' }}>
        <h2>Taxi Demo</h2>
        <button onClick={() => setRole('passenger')}>Passenger</button>
        <button onClick={() => setRole('driver')}>Driver</button>
      </div>
    );
  }
  return role === 'passenger' ? <Passenger /> : <Driver />;
}
export default App;
