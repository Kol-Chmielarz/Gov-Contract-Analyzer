import axios from "axios";

const API_URL = "http://localhost:8000"; // Change this if hosted

export const getContracts = async (limit: number = 50, year?: number) => {
  const response = await axios.get(`${API_URL}/contracts`, {
    params: { limit, year },
  });
  return response.data;
};

export const getCategories = async () => {
  const response = await axios.get(`${API_URL}/contracts/categories`);
  return response.data;
};