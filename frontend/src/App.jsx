import { useState } from "react";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Patients from "./pages/Patients";
import Doctors from "./pages/Doctors";
import Rooms from "./pages/Rooms";
import Admissions from "./pages/Admissions";
import NewAdmission from "./pages/NewAdmission";
import ReceptionistChatbot from "./pages/ReceptionistChatbot";
import ChangePassword from "./pages/ChangePassword";

function App() {
  const [loggedIn, setLoggedIn] = useState(
    localStorage.getItem("loggedIn") === "true"
  );

  const [page, setPage] = useState("Dashboard");

  const logout = () => {
    localStorage.removeItem("loggedIn");
    setLoggedIn(false);
  };

  if (!loggedIn) {
    return <Login setLoggedIn={setLoggedIn} />;
  }

  const menuItems = [
    "Dashboard",
    "New Admission",
    "Patients",
    "Doctors",
    "Rooms",
    "Admissions",
    "Receptionist Chatbot",
    "Change Password",
  ];

  const renderPage = () => {
    if (page === "Dashboard") return <Dashboard />;
    if (page === "New Admission") return <NewAdmission />;
    if (page === "Patients") return <Patients />;
    if (page === "Doctors") return <Doctors />;
    if (page === "Rooms") return <Rooms />;
    if (page === "Admissions") return <Admissions />;
    if (page === "Receptionist Chatbot") return <ReceptionistChatbot />;
    if (page === "Change Password") return <ChangePassword />;
    return <Dashboard />;
  };

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <h2>MedCare</h2>
        <p className="role">Admin Panel</p>

        <nav>
          {menuItems.map((item) => (
            <button
              key={item}
              className={page === item ? "active" : ""}
              onClick={() => setPage(item)}
            >
              {item}
            </button>
          ))}
        </nav>

        <button className="logout-btn" onClick={logout}>
          Logout
        </button>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <h1>{page}</h1>
            <p>AI Hospital Management System</p>
          </div>
        </header>

        {renderPage()}
      </main>
    </div>
  );
}

export default App;