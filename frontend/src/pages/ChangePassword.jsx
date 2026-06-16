import { useState } from "react";
import api from "../api";

function ChangePassword() {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [message, setMessage] = useState("");

  const changePassword = async (e) => {
    e.preventDefault();
    setMessage("");

    try {
      const res = await api.post("/change-password", {
        old_password: oldPassword,
        new_password: newPassword,
      });

      setMessage(res.data.message);
      setOldPassword("");
      setNewPassword("");
    } catch (err) {
      setMessage("Old password is incorrect.");
    }
  };

  return (
    <div className="page-card small-card">
      <h2>Change Password</h2>
      <p>Update admin password securely.</p>

      {message && <div className="info-box">{message}</div>}

      <form onSubmit={changePassword}>
        <label>Old Password</label>
        <input
          type="password"
          value={oldPassword}
          onChange={(e) => setOldPassword(e.target.value)}
        />

        <label>New Password</label>
        <input
          type="password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
        />

        <button type="submit">Change Password</button>
      </form>
    </div>
  );
}

export default ChangePassword;