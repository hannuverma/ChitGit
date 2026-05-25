import axios from "axios";

const api = axios.create({
	baseURL: "http://localhost:8000",
	// baseURL: "https://chitgit-1.onrender.com",
	withCredentials: true,
	headers: {
		"Content-Type": "application/json",
	},
});

export default api;
