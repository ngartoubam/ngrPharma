import axios from "axios";

const http = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    timeout: 20000,
});

http.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

http.interceptors.response.use(
    (res) => res,
    async (err) => {
        // (Option simple) si 401 => logout manuel
        return Promise.reject(err);
    }
);

export default http;
