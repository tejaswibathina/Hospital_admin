import { useEffect, useState } from "react";
import api from "../api";

function Dashboard() {
  const [data, setData] = useState(null);

  const loadDashboard = async () => {
    const res = await api.get("/dashboard");
    setData(res.data);
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  if (!data) {
    return <p>Loading dashboard...</p>;
  }

  return (
    <div className="page">
      <div className="cards-grid">
        <div className="card">
          <h3>Total Patients</h3>
          <h2>{data.total_patients}</h2>
        </div>

        <div className="card">
          <h3>Available Rooms</h3>
          <h2>{data.available_rooms}</h2>
        </div>

        <div className="card">
          <h3>Booked Rooms</h3>
          <h2>{data.booked_rooms}</h2>
        </div>

        <div className="card">
          <h3>Occupied Rooms</h3>
          <h2>{data.occupied_rooms}</h2>
        </div>

        <div className="card">
          <h3>Available Doctors</h3>
          <h2>{data.available_doctors}</h2>
        </div>

        <div className="card">
          <h3>Active Admissions</h3>
          <h2>{data.active_admissions}</h2>
        </div>
      </div>
    </div>
  );
}


import { useEffect, useState } from "react";
import api from "../api";

function Dashboard() {
  const [data, setData] = useState(null);

  const loadDashboard = async () => {
    const res = await api.get("/dashboard");
    setData(res.data);
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  if (!data) {
    return <p>Loading dashboard...</p>;
  }

  return (
    <div className="page">
      <div className="cards-grid">
        <div className="card">
          <h3>Total Patients</h3>
          <h2>{data.total_patients}</h2>
        </div>

        <div className="card">
          <h3>Available Rooms</h3>
          <h2>{data.available_rooms}</h2>
        </div>

        <div className="card">
          <h3>Booked Rooms</h3>
          <h2>{data.booked_rooms}</h2>
        </div>

        <div className="card">
          <h3>Occupied Rooms</h3>
          <h2>{data.occupied_rooms}</h2>
        </div>

        <div className="card">
          <h3>Available Doctors</h3>
          <h2>{data.available_doctors}</h2>
        </div>

        <div className="card">
          <h3>Active Admissions</h3>
          <h2>{data.active_admissions}</h2>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;