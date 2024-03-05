import React from "react";
import StatusBar from "./StatusBar";
import PriceChart from "./PriceChart";
const MiddleScreen = () => {
  return (
    <div className="flex flex-col bg-background w-full justify-between ml-4 gap-8">
      <PriceChart />
      <StatusBar />
    </div>
  );
};

export default MiddleScreen;
