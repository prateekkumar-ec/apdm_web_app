import axios from "axios";
import ENV from "../config/env.config";

const backend = axios.create({
  baseURL: ENV.API_BASE_URL,
});

export default backend;
