import React, { useState, useEffect } from 'react';
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
function Passenger() {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState(null);
  const [ride, setRide] = useState(null);
  const [ws, setWs] = useState(null);
  const login = async () => {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, password })
    });
    const data = await res.json();
    setToken(data.access_token);
  };
  const createRide = async () => {
    const res = await fetch(`${API_URL}/rides`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ pickup: 'Point A', destination: 'Point B' })
    });
    const data = await res.json();
    setRide(data);
  };
  useEffect(() => {
    if (token && ride) {
      const socket = new WebSocket(`${API_URL.replace('http','ws')}/ws/${ride.id}?token=${token}`);
      socket.onmessage = (e) => { console.log('WS:', e.data); };
      setWs(socket);
      return () => socket.close();
    }
  }, [token, ride]);
  if (!token) {
    return (
      <div>
        <h3>Passenger Login</h3>
        <input placeholder="Phone" value={phone} onChange={e => setPhone(e.target.value)} />
        <input placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
        <button onClick={login}>Login</button>
      </div>
    );
  }
  return (
    <div>
      <h3>Passenger Dashboard</h3>
      <button onClick={createRide}>Create Ride</button>
      <pre>{JSON.stringify(ride, null, 2)}</pre>
    </div>
  );
}
export default Passenger;
