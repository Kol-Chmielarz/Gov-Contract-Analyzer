"use client";
import { useState, useEffect } from "react";
import axios from "axios";

export default function MLPredictions() {
  // State for user inputs
  const [agency, setAgency] = useState("");
  const [fundingAgency, setFundingAgency] = useState("");
  const [contractCategory, setContractCategory] = useState<string>("");
  const [placeOfPerformance, setPlaceOfPerformance] = useState("");
  const [awardingSubAgency, setAwardingSubAgency] = useState("");
  const [fundingSubAgency, setFundingSubAgency] = useState("");
  const [contractDuration, setContractDuration] = useState("");
  const [predictedAmount, setPredictedAmount] = useState<number | null>(null);

  // Dropdown options state
  const [agencies, setAgencies] = useState<string[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [places, setPlaces] = useState<string[]>([]);
  const contractDurations = ["30", "60", "90", "120", "180", "365", "730", "1095"];

  // Fetch dropdown options from API
  useEffect(() => {
    axios.get("http://localhost:8000/api/contracts/agency-funding")
      .then(response => {
        const agencyData = response.data.map((item: any) => item.agency);
        setAgencies(agencyData);
      })
      .catch(error => console.error("Error fetching agencies:", error));

    axios.get("http://localhost:8000/api/contracts/category-breakdown")
      .then(response => {
        const filteredCategories = response.data
            .map((item: any) => item.contract_category)
            .filter((category: string) => !["BPA CALL", "PO", "DO", "DCA"].includes(category)); // Remove duplicates
        setCategories(filteredCategories);
      })
      .catch(error => console.error("Error fetching contract categories:", error));

    axios.get("http://localhost:8000/api/contracts/place-performance")
      .then(response => setPlaces(response.data.map((item: any) => item.place_of_performance)))
      .catch(error => console.error("Error fetching places:", error));
  }, []);

  // Predict award amount
  const predictAwardAmount = async () => {
    try {
      const response = await axios.get("http://localhost:8000/api/ml/predict-award", {
        params: {
          agency,
          category: contractCategory,
          place: placeOfPerformance,
          funding_agency: fundingAgency,
          awarding_sub_agency: awardingSubAgency,
          funding_sub_agency: fundingSubAgency,
          contract_duration: parseInt(contractDuration), // Convert string to int
        },
      });
      setPredictedAmount(response.data.predicted_award_amount);
    } catch (error) {
      console.error("Error predicting award amount:", error);
    }
  };

  return (
    <div className="bg-gray-900 text-white p-6 rounded-lg shadow-lg w-full max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-4 text-center">🔮 Predict Award Amount</h2>
      
      <div className="flex flex-col md:flex-row gap-6">
        {/* Prediction Form */}
        <div className="md:w-2/3 space-y-4">
          {/* Agency Dropdown */}
          <label className="block">
            <span className="text-gray-300">Agency:</span>
            <select
              className="w-full p-2 bg-gray-800 border border-gray-600 rounded"
              value={agency}
              onChange={(e) => setAgency(e.target.value)}
            >
              <option value="">Select Agency</option>
              {agencies.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          </label>

          {/* Funding Agency Dropdown */}
          <label className="block">
            <span className="text-gray-300">Funding Agency:</span>
            <select
              className="w-full p-2 bg-gray-800 border border-gray-600 rounded"
              value={fundingAgency}
              onChange={(e) => setFundingAgency(e.target.value)}
            >
              <option value="">Select Funding Agency</option>
              {agencies.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          </label>

          {/* Contract Category Dropdown */}
          <label className="block">
            <span className="text-gray-300">Contract Category:</span>
            <select
              className="w-full p-2 bg-gray-800 border border-gray-600 rounded"
              value={contractCategory}
              onChange={(e) => setContractCategory(e.target.value)}
            >
              <option value="">Select Contract Category</option>
              {categories.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </label>

          {/* Place of Performance Dropdown */}
          <label className="block">
            <span className="text-gray-300">Place of Performance:</span>
            <select
              className="w-full p-2 bg-gray-800 border border-gray-600 rounded"
              value={placeOfPerformance}
              onChange={(e) => setPlaceOfPerformance(e.target.value)}
            >
              <option value="">Select Place</option>
              {places.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </label>

          {/* Awarding Sub-Agency Dropdown */}
          <label className="block">
            <span className="text-gray-300">Awarding Sub-Agency:</span>
            <select
              className="w-full p-2 bg-gray-800 border border-gray-600 rounded"
              value={awardingSubAgency}
              onChange={(e) => setAwardingSubAgency(e.target.value)}
            >
              <option value="">Select Awarding Sub-Agency</option>
              {agencies.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          </label>

          {/* Funding Sub-Agency Dropdown */}
          <label className="block">
            <span className="text-gray-300">Funding Sub-Agency:</span>
            <select
              className="w-full p-2 bg-gray-800 border border-gray-600 rounded"
              value={fundingSubAgency}
              onChange={(e) => setFundingSubAgency(e.target.value)}
            >
              <option value="">Select Funding Sub-Agency</option>
              {agencies.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          </label>

          {/* Contract Duration Dropdown */}
          <label className="block">
            <span className="text-gray-300">Contract Duration (Days):</span>
            <select
              className="w-full p-2 bg-gray-800 border border-gray-600 rounded"
              value={contractDuration}
              onChange={(e) => setContractDuration(e.target.value)}
            >
              <option value="">Select Duration</option>
              {contractDurations.map((duration) => (
                <option key={duration} value={duration}>{duration} Days</option>
              ))}
            </select>
          </label>

          {/* Predict Button */}
          <button className="w-full mt-4 bg-yellow-400 text-black font-bold py-2 rounded" onClick={predictAwardAmount}>
            Predict Award Amount
          </button>

          {/* Prediction Result */}
          {predictedAmount !== null && (
            <p className="mt-4 text-center text-lg">
              💰 Predicted Award Amount: <span className="text-yellow-400 font-bold">${predictedAmount.toLocaleString()}</span>
            </p>
          )}
        </div>

        {/* Explanation Section */}
        <div className="md:w-1/3 p-4 bg-gray-800 rounded-lg shadow-md">
          <h3 className="text-lg font-bold text-center mb-2">How is the Award Amount Predicted?</h3>
          <p className="text-gray-300 text-sm">
          The award amount prediction model is built using a Random Forest Regressor, trained on 
            historical government contract data. It analyzes various factors such as:
         </p>
         <ul className="list-disc list-inside text-gray-300 text-sm mt-2">
            <li>Contract Duration (in days)</li>
            <li>Agency & Funding Agency</li>
            <li>Place of Performance</li>
            <li>Awarding & Funding Sub-Agencies</li>
          </ul>
          <p className="text-gray-300 text-sm mt-2">
            The model uses numerical encoding and past contract trends to predict the expected award 
            amount, aiding in data-driven funding estimates for contracts.
          </p>
        </div>
      </div>
    </div>
  );
}