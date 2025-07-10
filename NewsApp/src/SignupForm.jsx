import React, { useState } from 'react';

const SignupForm = ({ onSignup, switchToLogin }) => {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('http://localhost:5001/api/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, username, password })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Signup failed');
      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        onSignup();
      }, 1200);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <h2>Sign Up</h2>
      <input type="text" placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} required />
      <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
      <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required />
      {error && <div className="auth-error">{error}</div>}
      {success && <div className="auth-success">Signup successful! Redirecting...</div>}
      <button type="submit" disabled={loading}>{loading ? 'Signing up...' : 'Sign Up'}</button>
      <div className="auth-switch">Already have an account? <span onClick={switchToLogin}>Login</span></div>
    </form>
  );
};

export default SignupForm; 