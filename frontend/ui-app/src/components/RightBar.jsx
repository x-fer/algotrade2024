import React from "react";
import PriceChart from "./PriceChart";
import Order from "./Order";
import OrdersList from "./OrdersList";
import Settings from "./Settings";
const RightBar = () => {
  return (
    <div className="flex flex-col justify-between w-1/3 ml-4 bg-background">
      <div>
        <Order />

        <OrdersList />
      </div>

      <Settings />
    </div>
  );
};

export default RightBar;
