import React, { useState } from "react";
import PriceChart from "./PriceChart";
import SelectFuelBar from "./SelectResourceBar";
import Order from "./Order";
import OrdersList from "./OrdersList";
const RightBar = () => {
  return (
    <div className="flex flex-col bg-black-gray w-1/3 border-white border-l-2 p-4">
      <PriceChart />

      <Order />
      <OrdersList
        orders={[
          { id: 1 },
          { id: 2 },
          { id: 3 },
          { id: 4 },
          { id: 5 },
          { id: 6 },
        ]}
      />
    </div>
  );
};

export default RightBar;
