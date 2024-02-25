import React from "react";
import PriceChart from "./PriceChart";
import SelectFuelBar from "./SelectFuelBar";
import BuySell from "./BuySell";
const RightBar = () => {
  return (
    <div className="flex flex-col bg-black-gray w-1/4 border-white border-l-2 p-4">
      <PriceChart />
      <SelectFuelBar />
      <BuySell />
    </div>
  );
};

export default RightBar;
