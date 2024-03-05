import React, { useState } from "react";
import SelectPowerPlant from "./SelectPowerPlant";

const PowerPlantTypes = [
  "Biomass",
  "Coal",
  "Gas",
  "Geothermal",
  "Hydro",
  "Oil",
  "Nuclear",
  "Solar",
  "Wind",
];

const LeftBar = () => {
  const [selectedType, setSelectedType] = useState("");

  return (
    <div className="flex flex-col justify-around h-full p-4 gap-4 bg-primary rounded-3xl ">
      {PowerPlantTypes.map((type) => (
        <SelectPowerPlant
          key={type}
          type={type}
          active={selectedType == type ? true : false}
          setSelectedType={setSelectedType}
        />
      ))}
    </div>
  );
};

export default LeftBar;
