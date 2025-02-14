"use client";
import { useState } from "react";
import MonthlyTrends from "./components/MonthlyTrends";
import LocationCategoryTrends from "./components/LocationCategoryTrends";
import MLPredictions from "./components/MLPredictions";
import NotesCarousel from "./components/NotesCycle";

export default function Home() {
  const [selectedTab, setSelectedTab] = useState("monthly");

  return (
    <main className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="flex justify-between items-center p-6">
        <h1 className="text-2xl font-bold italic">
          <span className="text-white">Developed By</span>-<span className="text-yellow-400">Kol Chmielarz</span>
        </h1>
        <nav className="flex gap-4">
          <select
            className="border border-gray-500 px-4 py-2 rounded-md bg-black text-white"
            value={selectedTab}
            onChange={(e) => setSelectedTab(e.target.value)}
          >
            <option value="monthly">📊 Monthly Trends</option>
            <option value="location-category">🌍 Location & Contract Share</option>
            <option value="ml-insights">🤖 ML Predictions</option>
          </select>
        </nav>
      </header>

      {/* Title Section */}
      <section className="text-center py-16">
        <h2 className="text-4xl font-bold max-w-4xl mx-auto">
          Government Defense Contract Analyzation and Prediction
        </h2>
      </section>

      {/* Dynamic Content Based on Selected Tab */}
      {selectedTab === "monthly" && (
        <section className="mt-10 px-6 flex flex-col items-center">
          <h2 className="text-2xl font-bold text-center mb-6">📊 Monthly Contract Trends</h2>

          {/* Layout: Graphs on Left, Notes on Right */}
          <div className="flex flex-wrap md:flex-nowrap justify-between items-center gap-6 mt-6 w-full max-w-6xl">
            <div className="w-full md:w-2/3 flex flex-col justify-center">
              <MonthlyTrends />
            </div>
            <div className="w-full md:w-1/3 flex items-center justify-center">
              <div className="border-l border-gray-600 pl-6">
                <NotesCarousel />
              </div>
            </div>
          </div>
        </section>
      )}

      {selectedTab === "location-category" && (
        <section className="mt-10 px-6 flex flex-col items-center">
          <h2 className="text-2xl font-bold text-center mb-6">🌍 Location & Contract Share</h2>
          <LocationCategoryTrends />
        </section>
      )}

      {selectedTab === "ml-insights" && (
        <section className="mt-10 px-6 flex flex-col items-center">
          <h2 className="text-2xl font-bold text-center mb-6">🤖 Machine Learning Insights</h2>
          <MLPredictions />
        </section>
      )}

      {/* Page Description Section */}
      <section className="mt-10 px-6 flex justify-center">
        <p className="text-lg text-gray-300 max-w-3xl text-center">
          This page provides insights into government defense contracts, including trends, statistics, and predictive analysis. 
          Contracts and data have been collected using usaspending.gov and their free API.
        </p>
      </section>
    </main>
  );
}