import { useEffect, useState } from "react";
import api from "../api";

function Admissions() {
  const [admissions, setAdmissions] = useState([]);

  const loadAdmissions = async () => {
    const res = await api.get("/admissions");
    setAdmissions(res.data);
  };

  const deleteAdmission = async (admissionId) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this admission?"
    );

    if (!confirmDelete) return;

    const res = await api.post("/delete-admission", {
      admission_id: admissionId,
    });

    alert(res.data.message);
    loadAdmissions();
  };

  useEffect(() => {
    loadAdmissions();
  }, []);

  return (
    <div className="page-card">
      <h2>Admission Records</h2>
      <p>View all patient admission details.</p>

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Patient</th>
            <th>Room</th>
            <th>Room Type</th>
            <th>Doctor</th>
            <th>Specialization</th>
            <th>Insurance</th>
            <th>Date</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {admissions.map((admission) => (
            <tr key={admission.admission_id}>
              <td>{admission.admission_id}</td>
              <td>{admission.patient_name}</td>
              <td>{admission.room_number}</td>
              <td>{admission.room_type}</td>
              <td>{admission.doctor_name}</td>
              <td>{admission.specialization}</td>
              <td>{admission.insurance_provider}</td>
              <td>{admission.admission_date}</td>
              <td>
                <span className={`status ${admission.status.toLowerCase()}`}>
                  {admission.status}
                </span>
              </td>
              <td>
                <button
                  className="delete-btn"
                  onClick={() => deleteAdmission(admission.admission_id)}
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

export default Admissions;