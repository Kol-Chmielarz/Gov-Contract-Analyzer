import { useEffect, useState } from "react";
import { getContracts } from "../utils/api";
import { Bar } from "react-chartjs-2";

export default function Home() {
  const [contracts, setContracts] = useState([]);
  const [year, setYear] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    getContracts(50, year ?? undefined)
      .then((data) => setContracts(data))
      .catch((err) => setError("Failed to fetch contracts. Try again later."))
      .finally(() => setLoading(false));
  }, [year]);

  const chartData = {
    labels: contracts.map((c: any) => c.contract_id),
    datasets: [
      {
        label: "Award Amount",
        data: contracts.map((c: any) => c.award_amount),
        backgroundColor: "rgba(75, 192, 192, 0.6)",
      },
    ],
  };

  return (
    <div className="min-h-screen p-10 bg-gray-100">
      <h1 className="text-3xl font-bold mb-4">Federal Contracts</h1>

      <select
        className="mb-4 p-2 border"
        onChange={(e) => setYear(e.target.value ? Number(e.target.value) : null)}
      >
        <option value="">All Years</option>
        {Array.from({ length: 30 }, (_, i) => 1995 + i).map((yr) => (
          <option key={yr} value={yr}>
            {yr}
          </option>
        ))}
      </select>

      {loading ? <p>Loading contracts...</p> : null}
      {error ? <p className="text-red-500">{error}</p> : null}

      <div className="bg-white p-6 rounded-lg shadow-lg">
        {contracts.length > 0 ? (
          <Bar data={chartData} key={year || "all"} />
        ) : (
          <p>No contract data available.</p>
        )}
      </div>
    </div>
  );
}