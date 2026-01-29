import axios from "axios";

const backend = axios.create({
  baseURL: "http://127.0.0.1:8000", // FastAPI backend
});

export default backend;
