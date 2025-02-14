"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

// Globally set all chart text to white (helps on dark backgrounds)
ChartJS.defaults.color = "#ffffff";

interface ContractCategory {
  contract_category: string;
  contract_percentage: number;
  
}

export default function ContractCategoryTrends() {
  const [data, setData] = useState<ContractCategory[]>([]);

  useEffect(() => {
    axios.get("http://localhost:8000/api/contracts/category-breakdown")
      .then(response => {
        console.log("Category Breakdown Data:", response.data);
        // Filter out "DO" if desired
        const filteredData = response.data.filter(
          (item: ContractCategory) => item.contract_category !== "DO"
        );
        setData(filteredData);
      })
      .catch(error => console.error("Error fetching category trends:", error));
  }, []);

  // Prepare the Pie chart data
  const pieData = {
    labels: data.map(item => item.contract_category),
    datasets: [
      {
        label: "Contract Share (%)",
        data: data.map(item => item.contract_percentage),
        backgroundColor: [
          "#FF6384",
          "#36A2EB",
          "#FFCE56",
          "#4BC0C0",
          "#9966FF",
          "#FF9F40",
          "#C9CBCF",
          "#FF6384", 
        ],
      },
    ],
  };

  // Basic Pie chart options
  const pieOptions = {
    plugins: {
      legend: {
        labels: {
          color: "#ffffff", 
        },
      },
      tooltip: {
        callbacks: {
          label: (tooltipItem: any) => {
            const val = tooltipItem.raw;
            return `Contract Share: ${val.toFixed(2)}%`;
          },
        },
      },
    },
  };

  return (
    <div className="bg-gray-900 text-white p-6 rounded-lg shadow-lg">
      <h2 className="text-lg font-bold text-center">Contract Category Breakdown (%)</h2>
      {data.length > 0 ? (
        <Pie data={pieData} options={pieOptions} />
      ) : (
        <p className="text-center text-gray-400">Loading data or no data available...</p>
      )}
    </div>
  );
}