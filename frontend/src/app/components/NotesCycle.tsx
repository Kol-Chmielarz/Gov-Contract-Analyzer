"use client";
import { useEffect, useState } from "react";

const notes = [
  "New data sheds further light on how September has become a 'spending spree' season for defense agencies to get contract obligations out the door. (Source: Washington Technology and The Rhythm of Government Spending)",
  "The Federal Government’s fiscal year begins on October 1st and ends on September 30th of the next year. The fourth quarter (July–September) sees a surge in spending as agencies rush to use remaining budgets. (Source: FedBizAccess Strategic Contracting Solutions)",
];

export default function NotesCarousel() {
    const [index, setIndex] = useState(0);
  
    useEffect(() => {
      const interval = setInterval(() => {
        setIndex((prevIndex) => (prevIndex + 1) % notes.length);
      }, 5000); // Change note every 5 seconds
      return () => clearInterval(interval);
    }, []);
  
    return (
      <div className="flex items-center justify-center h-full p-6 border-l border-gray-600 text-sm text-gray-400 italic">
        <p className="transition-opacity duration-500 leading-6 max-w-xs">📌 {notes[index]}</p>
      </div>
    );
  }