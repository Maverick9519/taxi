import React, { useState, useEffect } from 'react';
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
function Driver() {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState(null);
  const [rides, setRides] = useState([]);
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
  useEffect(() => {
    if (token) {
      const socket = new WebSocket(`${API_URL.replace('http','ws')}/ws/driver_id?token=${token}`);
      socket.onmessage = (e) => {
        const msg = JSON.parse(e.data);
        console.log('WS Driver:', msg);
        setRides(prev => [...prev, msg]);
      };
      setWs(socket);
      return () => socket.close();
    }
  }, [token]);
  const acceptRide = async (ride_id) => {
    await fetch(`${API_URL}/rides/${ride_id}/accept`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }
    });
  };
  if (!token) {
    return (
      <div>
        <h3>Driver Login</h3>
        <input placeholder="Phone" value={phone} onChange={e => setPhone(e.target.value)} />
        <input placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
        <button onClick={login}>Login</button>
      </div>
    );
  }
  return (
    <div>
      <h3>Driver Dashboard</h3>
      <ul>
        {rides.map((r,i) => (
          <li key={i}>
            {JSON.stringify(r)}
            <button onClick={() => acceptRide(r.ride_id)}>Accept</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
export default Driver;
