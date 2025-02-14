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

    if (!data || data.length === 0) return <p className="text-center text-white">Loading data...</p>;

    // Sorting top 10 states by contract count
    const topStates = [...data].sort((a, b) => b.contract_count - a.contract_count).slice(0, 10);

    // Calculate total contract count for **all** states
    const totalContracts = data.reduce((sum, state) => sum + state.contract_count, 0);

    // Convert counts into percentages
    const contractPercentages = topStates.map(d => (totalContracts > 0 ? (d.contract_count / totalContracts) * 100 : 0));

    // Chart Data
    const barChartData = {
        labels: topStates.map(d => d.place_of_performance.trim()),
        datasets: [
            {
                label: "Contract Share (%)",
                data: contractPercentages,
                backgroundColor: "rgba(75, 192, 192, 0.6)",
                borderColor: "rgba(75, 192, 192, 1)",
                borderWidth: 1,
                barThickness: 30,  // ✅ Increase bar width
            },
        ],
    };

    // ✅ Fix: Ensure all labels are displayed properly
    const barChartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                ticks: {
                    color: "#ffffff",
                    font: { size: 12 },  // ✅ Reduce font size slightly
                    autoSkip: false, // ✅ Force all labels to be shown
                },
            },
            x: {
                ticks: {
                    color: "#ffffff",
                    font: { size: 12 }, // ✅ Adjust for better fit
                    autoSkip: false,  // ✅ Ensure no labels are hidden
                    maxRotation: 0, // ✅ Keep labels horizontal
                    minRotation: 0,
                },
            },
        },
        plugins: {
            legend: {
                labels: {
                    color: "#ffffff",
                },
            },
        },
    };

    return (
        <div className="bg-gray-900 text-white p-6 rounded-lg shadow-lg w-full" style={{ height: "600px", maxWidth: "1000px", margin: "auto" }}>
            <h2 className="text-lg font-bold text-center">📍 Top States by Contract Share (%)</h2>
            <Bar data={barChartData} options={barChartOptions} />
        </div>
    );
}