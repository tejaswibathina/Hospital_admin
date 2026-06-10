import { useState } from "react";
import api from "../api";

function NewAdmission() {
  const [form, setForm] = useState({
    patient_name: "",
    age: "",
    gender: "Male",
    phone: "",
    address: "",
    room_type: "General",
    specialization: "ENT",
    insurance_provider: "LIC",
  });

  const [message, setMessage] = useState("");

  const updateForm = (field, value) => {
    setForm({
      ...form,
      [field]: value,
    });
  };

  const submitAdmission = async (e) => {
    e.preventDefault();
    setMessage("");

    if (!form.patient_name || !form.phone || !form.age) {
      setMessage("Please fill patient name, age and phone number.");
      return;
    }

    try {
      const res = await api.post("/admit-patient", {
        ...form,
        age: Number(form.age),
      });

      setMessage(res.data.message);
    } catch (err) {
      setMessage("Failed to admit patient.");
    }
  };

  return (
    <div className="page-card">
      <h2>New Patient Admission</h2>
      <p>Fill patient and admission details.</p>

      {message && <div className="info-box">{message}</div>}

      <form className="form-grid" onSubmit={submitAdmission}>
        <div>
          <label>Patient Name</label>
          <input
            value={form.patient_name}
            onChange={(e) => updateForm("patient_name", e.target.value)}
          />
        </div>

        <div>
          <label>Age</label>
          <input
            type="number"
            value={form.age}
            onChange={(e) => updateForm("age", e.target.value)}
          />
        </div>

        <div>
          <label>Gender</label>
          <select
            value={form.gender}
            onChange={(e) => updateForm("gender", e.target.value)}
          >
            <option>Male</option>
            <option>Female</option>
            <option>Other</option>
          </select>
        </div>

        <div>
          <label>Phone</label>
          <input
            value={form.phone}
            onChange={(e) => updateForm("phone", e.target.value)}
          />
        </div>

        <div className="full">
          <label>Address</label>
          <textarea
            value={form.address}
            onChange={(e) => updateForm("address", e.target.value)}
          />
        </div>

        <div>
          <label>Room Type</label>
          <select
            value={form.room_type}
            onChange={(e) => updateForm("room_type", e.target.value)}
          >
            <option>General</option>
            <option>Deluxe</option>
            <option>Luxury</option>
          </select>
        </div>

        <div>
          <label>Specialization</label>
          <select
            value={form.specialization}
            onChange={(e) => updateForm("specialization", e.target.value)}
          >
            <option>ENT</option>
            <option>Dentist</option>
            <option>Cardiologist</option>
            <option>Pediatrician</option>
            <option>Dermatologist</option>
          </select>
        </div>

        <div>
          <label>Insurance Provider</label>
          <select
            value={form.insurance_provider}
            onChange={(e) => updateForm("insurance_provider", e.target.value)}
          >
            <option>LIC</option>
            <option>AIG</option>
            <option>Indian</option>
            <option>SBI</option>
          </select>
        </div>

        <button type="submit">Admit Patient</button>
      </form>
    </div>
  );
}

export default NewAdmission;