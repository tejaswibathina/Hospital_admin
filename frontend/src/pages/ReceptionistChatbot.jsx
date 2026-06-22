 import { useState } from "react";
import api from "../api";

function ReceptionistChatbot() {
  const [input, setInput] = useState("");

  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Hello 👋 Welcome to MedCare Hospital. How may I help you today?",
    },
  ]);

  const [sessionId] = useState(() => {
    let id = localStorage.getItem("hospital_session");

    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem("hospital_session", id);
    }

    return id;
  });

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      sender: "user",
      text: input,
    };

    setMessages((prev) => [...prev, userMessage]);

    const currentInput = input;
    setInput("");

    try {
      const response = await api.post("/chat", {
        message: currentInput,
        session_id: sessionId,
      });

      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: response.data.reply || "No response received.",
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "Sorry, I couldn't connect to the AI assistant.",
        },
      ]);

      console.error(error);
    }
  };

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
          onChange={(e) => setInput(e.target.value)}
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

export default ReceptionistChatbot;