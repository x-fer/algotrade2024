import React, { useState } from "react";
import PriceChart from "./PriceChart";
import SelectFuelBar from "./SelectFuelBar";
import BuySell from "./BuySell";
const RightBar = () => {
  const [quantity, setQuantity] = useState(0);

  return (
    <div className="flex flex-col bg-black-gray w-1/3 border-white border-l-2 p-4">
      <PriceChart />
      <SelectFuelBar />
      <BuySell quantity={quantity} setQuantity={setQuantity} />
    </div>
  );
};

export default RightBar;
