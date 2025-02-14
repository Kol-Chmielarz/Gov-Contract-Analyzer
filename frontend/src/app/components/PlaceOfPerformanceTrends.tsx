"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import { Bar } from "react-chartjs-2";

export default function PlaceOfPerformanceTrends() {
    const [data, setData] = useState<{ place_of_performance: string; contract_count: number; total_award: number }[]>([]);

    useEffect(() => {
        axios.get("http://localhost:8000/api/contracts/place-performance")
            .then((response) => setData(response.data))
            .catch((error) => console.error("Error fetching place performance trends:", error));
    }, []);

    // Ensure data is available
    if (!data || data.length === 0) return <p className="text-center text-white">Loading data...</p>;

    // Sorting top 10 states by contract count
    const topStates = [...data].sort((a, b) => b.contract_count - a.contract_count).slice(0, 10);

    // Calculate total contract count for **all** states
    const totalContracts = data.reduce((sum, state) => sum + state.contract_count, 0);

    // Convert counts into percentages
    const contractPercentages = topStates.map(d => (totalContracts > 0 ? (d.contract_count / totalContracts) * 100 : 0));

    // Chart Data
    const barChartData = {
        labels: topStates.map(d => d.place_of_performance),
        datasets: [
            {
                label: "Contract Share (%)",
                data: contractPercentages,
                backgroundColor: "rgba(75, 192, 192, 0.6)",
                borderColor: "rgba(75, 192, 192, 1)",
                borderWidth: 1,
            },
        ],
    };

    return (
        <div className="bg-gray-900 text-white p-6 rounded-lg shadow-lg w-full">
            <h2 className="text-lg font-bold text-center">Top 10 Locations by Contract Share (%)</h2>
            <Bar data={barChartData} />
        </div>
    );
}