import axios from "axios";

const API = axios.create({
    baseURL: "http://127.0.0.1:8000/api",
});

export const getFinanceDashboard = async () => {
    const response = await API.get("/bi/finance/");
    return response.data;
};
