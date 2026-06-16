import { useEffect, useState } from "react";
import api from "../api";

function Rooms() {
  const [rooms, setRooms] = useState([]);

  const loadRooms = async () => {
    const res = await api.get("/rooms");
    setRooms(res.data);
  };

  useEffect(() => {
    loadRooms();
  }, []);

  return (
    <div className="page-card">
      <h2>Room Status</h2>
      <p>View all hospital rooms and current availability.</p>

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Room Number</th>
            <th>Room Type</th>
            <th>Price Per Day</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {rooms.map((room) => (
            <tr key={room.room_id}>
              <td>{room.room_id}</td>
              <td>{room.room_number}</td>
              <td>{room.room_type}</td>
              <td>{room.price_per_day}</td>
              <td>
                <span className={`status ${room.status.toLowerCase()}`}>
                  {room.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Rooms;