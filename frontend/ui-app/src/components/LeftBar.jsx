import React from "react";
import SelectPowerPlant from "./SelectPowerPlant";

const LeftBar = () => {
  return (
    <div className="flex flex-col justify-around bg-black-gray h-full p-4 border-white border-r-2">
      <SelectPowerPlant type="Biomass" />
      <SelectPowerPlant type="Coal" />
      <SelectPowerPlant type="Gas" />
      <SelectPowerPlant type="Geothermal" />
      <SelectPowerPlant type="Hydro" />
      <SelectPowerPlant type="Oil" />
      <SelectPowerPlant type="Nuclear" />
      <SelectPowerPlant type="Solar" />
      <SelectPowerPlant type="Wind" />
    </div>
  );
};

export default LeftBar;
