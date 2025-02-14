"use client";
import { useState, useEffect } from "react";
import axios from "axios";

export default function UserInputPrediction() {
  const [agency, setAgency] = useState("");
  const [category, setCategory] = useState("");
  const [place, setPlace] = useState("");
  const [prediction, setPrediction] = useState<number | null>(null);

  // Dropdown options state
  const [agencies, setAgencies] = useState<string[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [places, setPlaces] = useState<string[]>([]);

  // Fetch dropdown options from API
  useEffect(() => {
    axios.get("http://localhost:8000/api/contracts/agency-funding")
      .then(response => setAgencies(response.data.map((item: any) => item.agency)))
      .catch(error => console.error("Error fetching agencies:", error));

    axios.get("http://localhost:8000/api/contracts/category-breakdown")
      .then(response => setCategories(response.data.map((item: any) => item.contract_category)))
      .catch(error => console.error("Error fetching contract categories:", error));

    axios.get("http://localhost:8000/api/contracts/place-performance")
      .then(response => setPlaces(response.data.map((item: any) => item.place_of_performance)))
      .catch(error => console.error("Error fetching places:", error));
  }, []);

  // Predict award amount
  const handlePredict = async () => {
    try {
      const res = await axios.get("http://localhost:8000/api/ml/predict-award", {
        params: { agency, category, place },
      });
      setPrediction(res.data.predicted_award_amount);
    } catch (error) {
      console.error("Error predicting award amount:", error);
    }
  };

  return (
    <div className="bg-gray-900 text-white p-6 rounded-lg shadow-lg w-full max-w-3xl mx-auto">
      <h3 className="text-2xl font-bold mb-4 text-center">🏆 Predict Award Amount</h3>

      {/* Dropdown Selectors */}
      <div className="space-y-4">
        <label className="block">
          <span className="text-gray-300">Agency:</span>
          <select className="w-full p-2 bg-gray-800 border border-gray-600 rounded" value={agency} onChange={(e) => setAgency(e.target.value)}>
            <option value="">Select Agency</option>
            {agencies.map((a) => <option key={a} value={a}>{a}</option>)}
          </select>
        </label>

        <label className="block">
          <span className="text-gray-300">Contract Category:</span>
          <select className="w-full p-2 bg-gray-800 border border-gray-600 rounded" value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">Select Contract Category</option>
            {categories.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </label>

        <label className="block">
          <span className="text-gray-300">Place of Performance:</span>
          <select className="w-full p-2 bg-gray-800 border border-gray-600 rounded" value={place} onChange={(e) => setPlace(e.target.value)}>
            <option value="">Select Place</option>
            {places.map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
        </label>
      </div>

      {/* Predict Button */}
      <button 
        className="w-full mt-4 bg-yellow-400 text-black font-bold py-2 rounded"
        onClick={handlePredict}
      >
        Predict Award Amount
      </button>

      {/* Prediction Result */}
      {prediction !== null && (
        <p className="mt-4 text-center text-lg">
          💰 Predicted Award Amount: <span className="text-yellow-400 font-bold">${prediction.toLocaleString()}</span>
        </p>
      )}
    </div>
  );
}