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

      <Settings />
    </div>
  );
};

export default RightBar;
