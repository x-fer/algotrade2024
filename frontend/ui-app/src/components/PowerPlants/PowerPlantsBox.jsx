import React, { useState } from "react";
import SelectPowerPlant from "./SelectPowerPlant";
import PowerPlantInfo from "./PowerPlantInfo";

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

const PowerPlantsBox = () => {
  const [selectedType, setSelectedType] = useState("");

  return (
    <div className="flex p-4 bg-primary rounded-3xl gap-4">
      <div className="flex flex-col justify-around h-full gap-4 bg-primary rounded-3xl ">
        {PowerPlantTypes.map((type) => (
          <SelectPowerPlant
            key={type}
            type={type}
            active={selectedType == type ? true : false}
            setSelectedType={setSelectedType}
          />
        ))}
      </div>

      <PowerPlantInfo />
    </div>
  );
};

export default PowerPlantsBox;
