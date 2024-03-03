import React from "react";
import PriceChart from "./PriceChart";
import Order from "./Order";
import OrdersList from "./OrdersList";
import Settings from "./Settings";
const RightBar = () => {
  return (
    <div className="flex flex-col bg-black-gray w-1/3 border-white border-l-2 p-4 justify-between">
      <div>
        <PriceChart />

        <Order />

        <OrdersList />
      </div>

      <Settings />
    </div>
  );
};

export default RightBar;
