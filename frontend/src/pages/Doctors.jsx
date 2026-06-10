import { useEffect, useState } from "react";
import api from "../api";

function Doctors() {
  const [doctors, setDoctors] = useState([]);

  const loadDoctors = async () => {
    const res = await api.get("/doctors");
    setDoctors(res.data);
  };

  useEffect(() => {
    loadDoctors();
  }, []);

  return (
    <div className="page-card">
      <h2>Doctor Allocation</h2>
      <p>View doctor department and availability status.</p>

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Doctor Name</th>
            <th>Specialization</th>
            <th>Phone</th>
            <th>Status</th>
            <th>Fee</th>
          </tr>
        </thead>

        <tbody>
          {doctors.map((doctor) => (
            <tr key={doctor.doctor_id}>
              <td>{doctor.doctor_id}</td>
              <td>{doctor.doctor_name}</td>
              <td>{doctor.specialization}</td>
              <td>{doctor.phone}</td>
              <td>
                <span
                  className={`status ${doctor.availability_status
                    .toLowerCase()
                    .replace(" ", "-")}`}
                >
                  {doctor.availability_status === "Busy"
                    ? "Allocated"
                    : doctor.availability_status}
                </span>
              </td>
              <td>{doctor.consultation_fee}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Doctors;