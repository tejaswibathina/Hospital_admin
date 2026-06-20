import { useEffect, useState } from "react";
import api from "../api";

function Patients() {
  const [patients, setPatients] = useState([]);

  const loadPatients = async () => {
    const res = await api.get("/patients");
    setPatients(res.data);
  };

  const deletePatient = async (patientId) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this patient?"
    );

    if (!confirmDelete) return;

    const res = await api.post("/delete-patient", {
      patient_id: patientId,
    });

    alert(res.data.message);
    loadPatients();
  };

  useEffect(() => {
    loadPatients();
  }, []);

  return (
    <div className="page-card">
      <h2>Patient Records</h2>
      <p>View and manage all registered patients.</p>

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Patient Name</th>
            <th>Age</th>
            <th>Gender</th>
            <th>Phone</th>
            <th>Address</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {patients.map((patient) => (
            <tr key={patient.patient_id}>
              <td>{patient.patient_id}</td>
              <td>{patient.patient_name}</td>
              <td>{patient.age}</td>
              <td>{patient.gender}</td>
              <td>{patient.phone}</td>
              <td>{patient.address}</td>
              <td>
                <button
                  className="delete-btn"
                  onClick={() => deletePatient(patient.patient_id)}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Patients;