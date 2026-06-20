import { useState } from "react";
import api from "../api";

function ReceptionistChatbot() {
  const [input, setInput] = useState("");

  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Hello 👋 Welcome to MedCare Hospital. How may I help you today?"
    }
  ]);

  const [sessionId] = useState(() => {
  let id = localStorage.getItem("hospital_session");

  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(
      "hospital_session",
      id
    );
  }

  return id;
});

  return (
    <div className="page-card">
      <h2>AI Receptionist</h2>

      <div className="chat-box">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={
              msg.sender === "bot"
                ? "bot-message"
                : "user-message"
            }
          >
            {msg.text}
          </div>
        ))}
      </div>

      <div className="chat-input">
        <input
          value={input}
          onChange={(e) =>
            setInput(e.target.value)
          }
          placeholder="Ask anything..."
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              sendMessage();
            }
          }}
        />

        <button onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  );
}

import { useState } from "react";
import api from "../api";

function ReceptionistChatbot() {
  const [step, setStep] = useState("name");
  const [input, setInput] = useState("");

  const [data, setData] = useState({});
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Hello, I am the hospital receptionist assistant. Please tell me the patient name.",
    },
  ]);

  const addMessage = (sender, text) => {
    setMessages((prev) => [...prev, { sender, text }]);
  };

  const resetChat = () => {
    setStep("name");
    setInput("");
    setData({});
    setMessages([
      {
        sender: "bot",
        text: "Hello, I am the hospital receptionist assistant. Please tell me the patient name.",
      },
    ]);
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const value = input.trim();
    addMessage("user", value);
    setInput("");

    if (step === "name") {
      setData({ ...data, patient_name: value });
      setStep("age");
      addMessage("bot", "Please enter the patient age.");
    }

    else if (step === "age") {
      if (isNaN(value)) {
        addMessage("bot", "Please enter a valid age in numbers.");
        return;
      }

      setData({ ...data, age: Number(value) });
      setStep("gender");
      addMessage("bot", "Please enter gender: Male, Female, or Other.");
    }

    else if (step === "gender") {
      const gender = value.charAt(0).toUpperCase() + value.slice(1).toLowerCase();

      if (!["Male", "Female", "Other"].includes(gender)) {
        addMessage("bot", "Please enter gender as Male, Female, or Other.");
        return;
      }

      setData({ ...data, gender });
      setStep("phone");
      addMessage("bot", "Please enter the patient phone number.");
    }

    else if (step === "phone") {
      if (!/^[0-9]{10,}$/.test(value)) {
        addMessage("bot", "Please enter a valid phone number with at least 10 digits.");
        return;
      }

      setData({ ...data, phone: value });
      setStep("address");
      addMessage("bot", "Please enter the patient address.");
    }

    else if (step === "address") {
      setData({ ...data, address: value });
      setStep("symptoms");
      addMessage("bot", "What problem or symptoms is the patient facing?");
    }

    else if (step === "symptoms") {
      const res = await api.post("/suggest-specialization", {
        message: value,
      });

      const specialization = res.data.specialization;

      setData({
        ...data,
        symptoms: value,
        specialization,
      });

      setStep("confirm_specialization");

      addMessage(
        "bot",
        `Based on the symptoms, suggested department is ${specialization}. Do you want to continue? Reply Yes or No.`
      );
    }

    else if (step === "confirm_specialization") {
      if (value.toLowerCase() === "yes" || value.toLowerCase() === "y") {
        setStep("room_type");
        addMessage("bot", "Please enter room type: General, Deluxe, or Luxury.");
      } else {
        setStep("manual_specialization");
        addMessage(
          "bot",
          "Please enter required specialization: ENT, Dentist, Cardiologist, Pediatrician, Dermatologist."
        );
      }
    }

    else if (step === "manual_specialization") {
      const allowed = ["ENT", "Dentist", "Cardiologist", "Pediatrician", "Dermatologist"];

      const formatted =
        value.toLowerCase() === "ent"
          ? "ENT"
          : value.charAt(0).toUpperCase() + value.slice(1).toLowerCase();

      if (!allowed.includes(formatted)) {
        addMessage("bot", "Please enter a valid specialization.");
        return;
      }

      setData({ ...data, specialization: formatted });
      setStep("room_type");
      addMessage("bot", "Please enter room type: General, Deluxe, or Luxury.");
    }

    else if (step === "room_type") {
      const roomType = value.charAt(0).toUpperCase() + value.slice(1).toLowerCase();

      if (!["General", "Deluxe", "Luxury"].includes(roomType)) {
        addMessage("bot", "Please enter valid room type: General, Deluxe, or Luxury.");
        return;
      }

      setData({ ...data, room_type: roomType });
      setStep("insurance");
      addMessage("bot", "Please enter insurance provider: LIC, AIG, Indian, or SBI.");
    }

    else if (step === "insurance") {
      let insurance = value.toUpperCase();

      if (insurance === "INDIAN") {
        insurance = "Indian";
      }

      if (!["LIC", "AIG", "Indian", "SBI"].includes(insurance)) {
        addMessage("bot", "Please enter valid insurance provider: LIC, AIG, Indian, or SBI.");
        return;
      }

      const finalData = {
        ...data,
        insurance_provider: insurance,
      };

      setData(finalData);
      setStep("final_confirm");

      addMessage(
        "bot",
        `Please confirm admission:
Patient: ${finalData.patient_name}
Age: ${finalData.age}
Gender: ${finalData.gender}
Phone: ${finalData.phone}
Address: ${finalData.address}
Symptoms: ${finalData.symptoms}
Doctor: ${finalData.specialization}
Room: ${finalData.room_type}
Insurance: ${finalData.insurance_provider}

Reply Yes to admit or No to cancel.`
      );
    }

    else if (step === "final_confirm") {
      if (value.toLowerCase() === "yes" || value.toLowerCase() === "y") {
        const res = await api.post("/admit-patient", data);

        addMessage("bot", res.data.message);
        setStep("completed");
      } else {
        addMessage("bot", "Admission cancelled.");
        setStep("completed");
      }
    }

    else {
      addMessage("bot", "This chat is completed. Click Start New Chat to admit another patient.");
    }
  };

  return (
    <div className="page-card">
      <h2>Receptionist Chatbot</h2>
      <p>
        The chatbot asks patient details, symptoms, suggests doctor and admits the patient.
      </p>

      <button className="secondary-btn" onClick={resetChat}>
        Start New Chat
      </button>

      <div className="chat-box">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={msg.sender === "bot" ? "bot-message" : "user-message"}
          >
            {msg.text}
          </div>
        ))}
      </div>

      <div className="chat-input">
        <input
          value={input}
          placeholder="Type your reply..."
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleSend();
            }
          }}
        />

        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}

export default ReceptionistChatbot;