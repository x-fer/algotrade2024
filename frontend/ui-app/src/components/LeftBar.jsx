import React from "react";
import SelectPowerPlant from "./SelectPowerPlant";

const LeftBar = () => {
  return (
    <div className="flex flex-col justify-between bg-red-500 h-full pt-12 pb-12">
      <SelectPowerPlant type="Coal" />
      <SelectPowerPlant type="Gas" />
      <SelectPowerPlant type="Nuclear" />
      <SelectPowerPlant type="Solar" />
      <SelectPowerPlant type="Wind" />
      <SelectPowerPlant type="Hydro" />
    </div>
  );
};

export default LeftBar;
