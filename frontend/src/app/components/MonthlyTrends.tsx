"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import { Bar, Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, PointElement, LineElement, Title, Tooltip, Legend } from "chart.js";

// ✅ Register all required elements
ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, PointElement, LineElement, Title, Tooltip, Legend);
export default function MonthlyTrends() {
    const [data, setData] = useState<{ month: number; contract_count: number; median_award_amount: number }[]>([]);

    useEffect(() => {
        axios.get("http://localhost:8000/api/contracts/monthly-trends")
            .then((response) => setData(response.data))
            .catch((error) => console.error("Error fetching contract trends:", error));
    }, []);

    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

    // Convert values to percentages for contract count
    const totalContracts = data.reduce((sum, d) => sum + d.contract_count, 0);
    const contractPercentages = data.map(d => totalContracts ? (d.contract_count / totalContracts) * 100 : 0);

    // Bar chart (Contract Count %)
    const barChartData = {
        labels: months,
        datasets: [
            {
                label: "Contract Count (%)",
                data: contractPercentages,
                backgroundColor: "rgba(75, 192, 192, 0.6)",
                borderColor: "rgba(75, 192, 192, 1)",
                borderWidth: 1,
            },
        ],
    };

    // Line chart (Actual $ Median Award Amount)
    const lineChartData = {
        labels: months,
        datasets: [
            {
                label: "Median Award Amount ($)",
                data: data.map(d => d.median_award_amount), // Keep actual dollar values
                borderColor: "rgba(255, 99, 132, 1)",
                borderWidth: 2,
                fill: false,
            },
        ],
    };

    return (
        <div className="bg-gray-900 text-white p-8 rounded-lg shadow-lg w-full max-w-5xl mx-auto">
            <h2 className="text-2xl font-bold mb-4 text-center"></h2>

            {/* Side-by-Side Graph Layout */}
            <div className="flex flex-wrap md:flex-nowrap justify-center gap-8">
                {/* Contract Count Graph */}
                <div className="w-full md:w-1/2">
                    <h3 className="text-lg font-semibold text-center">📅 Contract Count (%) Per Month</h3>
                    <Bar data={barChartData} />
                </div>

                {/* Median Award Amount Graph (in $) */}
                <div className="w-full md:w-1/2">
                    <h3 className="text-lg font-semibold text-center">💰 Median Award ($) By Month</h3>
                    <Line data={lineChartData} />
                </div>
            </div>
        </div>
    );
}