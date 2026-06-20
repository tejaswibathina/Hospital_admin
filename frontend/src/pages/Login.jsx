import { useState } from "react";
import api from "../api";

function Login({ setLoggedIn }) {
  const [username, setUsername] = useState("");
const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await api.post("/login", {
        username,
        password,
      });

      localStorage.setItem("loggedIn", "true");
      setLoggedIn(true);
    } catch (err) {
      setError("Invalid username or password");
    }
  };

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={handleLogin}>
        <h2>MedCare Login</h2>
        <p>Admin access only</p>

        {error && <div className="error">{error}</div>}

        <label>Username</label>
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button type="submit">Login</button>
      </form>
    </div>
  );
}

export default Login;

import { useState } from "react";
import api from "../api";

function Login({ setLoggedIn }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await api.post("/login", {
        username,
        password,
      });

      localStorage.setItem("loggedIn", "true");
      setLoggedIn(true);
    } catch (err) {
      setError("Invalid username or password");
    }
  };

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={handleLogin}>
        <h2>MedCare Login</h2>
        <p>Admin access only</p>

        {error && <div className="error">{error}</div>}

        <label>Username</label>
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button type="submit">Login</button>
      </form>
    </div>
  );
}

export default Login;
