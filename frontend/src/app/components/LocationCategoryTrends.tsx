"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import { Bar, Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend);
ChartJS.defaults.color = "#ffffff"; // Set all text to white for dark backgrounds

interface PlacePerformance {
  place_of_performance: string;
  contract_count: number;
}

interface ContractCategory {
  contract_category: string;
  contract_percentage: number;
}

export default function LocationCategoryTrends() {
  const [placeData, setPlaceData] = useState<PlacePerformance[]>([]);
  const [categoryData, setCategoryData] = useState<ContractCategory[]>([]);
  const [totalContracts, setTotalContracts] = useState<number>(0);

  useEffect(() => {
    axios.get("http://127.0.0.1:8000/api/contracts/place-performance")
      .then(response => {
        setPlaceData(response.data);
        const total = response.data.reduce((sum: number, d: PlacePerformance) => sum + d.contract_count, 0);
        setTotalContracts(total);
      })
      .catch(error => console.error("Error fetching place performance:", error));

    axios.get("http://127.0.0.1:8000/api/contracts/category-breakdown")
      .then(response => {
        const filteredData = response.data.filter(
          (item: ContractCategory) => item.contract_category !== "DO" && item.contract_category !== "DCA" && item.contract_category !== "PO" && item.contract_category !== "BPA"
        );
        setCategoryData(filteredData);
      })
      .catch(error => console.error("Error fetching contract categories:", error));
  }, []);

  // ✅ Prepare Bar Chart Data 
  const barData = {
    labels: placeData.map(d => d.place_of_performance),
    datasets: [
      {
        label: "Contract Share (%)",
        data: placeData.map(d =>
          totalContracts > 0 ? (d.contract_count / totalContracts) * 100 : 0
        ),
        backgroundColor: "rgba(75, 192, 192, 0.6)",
        borderColor: "rgba(75, 192, 192, 1)",
        borderWidth: 1,
      },
    ],
  };

  // ✅ Ensure all labels are displayed properly
  const barOptions = {
    indexAxis: "y" as const,
    responsive: true,
    maintainAspectRatio: false, // Prevents auto-shrinking
    scales: {
      y: {
        ticks: {
          autoSkip: false,  // ✅ Prevent Chart.js from skipping labels
          maxTicksLimit: 10, // ✅ Ensure all 10 states are labeled
          font: {
            size: 14, // ✅ Improve readability
          },
        },
      },
    },
    plugins: {
      legend: {
        labels: {
          color: "#ffffff", // Ensure white text for dark mode
          font: {
            size: 16, // Improve legend readability
          },
        },
      },
      tooltip: {
        callbacks: {
          label: function (tooltipItem: any) {
            const value = tooltipItem.raw;
            return `Contract Share: ${value.toFixed(2)}%`;
          },
        },
      },
    },
  };

  // ✅ Prepare Pie Chart Data
  const pieData = {
    labels: categoryData.map(d => d.contract_category),
    datasets: [
      {
        label: "Contract Share (%)",
        data: categoryData.map(d => d.contract_percentage),
        backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"],
      },
    ],
  };

  const pieOptions = {
    plugins: {
      legend: {
        labels: {
          color: "#ffffff",
        },
      },
      tooltip: {
        callbacks: {
          label: function (tooltipItem: any) {
            const value = tooltipItem.raw;
            return `Contract Share: ${value.toFixed(2)}%`;
          },
        },
      },
    },
  };

  return (
    <div className="text-white p-8">
      {/* Section Title */}
     

      {/* Flex Container: Bar on the left, Pie on the right (on medium+ screens) */}
      <div className="flex flex-wrap md:flex-nowrap gap-6 justify-center items-start">
        {/* Left: Top 10 Locations by Contract Share (%) */}
        <div className="w-full md:w-1/2">
          <h3 className="text-lg font-semibold mb-4 text-center">📍 Top States by Contract Share (%)</h3>
          <div className="w-full max-w-4xl h-[500px]"> {/* ✅ Increase height for better spacing */}
            <Bar data={barData} options={barOptions} />
          </div>
        </div>

        {/* Right: Contract Category Breakdown (%) */}
        <div className="w-full md:w-1/2">
          <h3 className="text-lg font-semibold mb-4 text-center">📑 Contract Category Breakdown (%)</h3>
          {categoryData.length > 0 ? (
            <Pie data={pieData} options={pieOptions} />
          ) : (
            <p className="text-center text-gray-400">Loading data or no data available...</p>
          )}
        </div>
      </div>
    </div>
  );
}