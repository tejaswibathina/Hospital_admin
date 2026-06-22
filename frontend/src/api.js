import axios from "axios";

const api = axios.create({
  baseURL: "https://hospital-admin-1-t3j6.onrender.com",
});

export default api;