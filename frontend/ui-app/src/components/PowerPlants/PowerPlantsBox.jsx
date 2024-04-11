import React, { useContext, useState } from "react";
import PowerPlantInfo from "./PowerPlantInfo";
import { DataContext } from "../DataProvider";

const PowerPlantTypes = [
  { key: "biomass", name: "Biomass" },
  { key: "coal", name: "Coal" },
  { key: "gas", name: "Gas" },
  { key: "oil", name: "Oil" },
  { key: "wind", name: "Wind" },
  { key: "solar", name: "Solar" },
  { key: "hydro", name: "Hydro" },
  { key: "geothermal", name: "Geothermal" },
  { key: "uranium", name: "Nuclear" },
];

const SelectPowerPlantButton = ({
  resource,
  active,
  setSelectedPowerPlant,
}) => {
  return (
    <button
      className={` hover:bg-tertiary active:bg-primary border-[3px]  text-white text-xl w-[8vw] h-full rounded-3xl ${
        active ? " border-red bg-tertiary" : "bg-secondary border-secondary"
      }`}
      onClick={() => setSelectedPowerPlant(resource)}
    >
      {resource.name}
    </button>
  );
};

const PowerPlantsBox = () => {
  const { selectedPowerPlant, setSelectedPowerPlant } = useContext(DataContext);

  return (
    <div className="flex p-4 gap-4 rounded-3xl bg-primary shadow-xl">
      <div className="flex flex-col justify-around h-full gap-4 bg-primary rounded-3xl ">
        {PowerPlantTypes.map((item) => (
          <SelectPowerPlantButton
            key={item.name}
            resource={item}
            active={selectedPowerPlant?.key === item.key ? true : false}
            setSelectedPowerPlant={setSelectedPowerPlant}
          />
        ))}
      </div>

      <PowerPlantInfo />
    </div>
  );
};

export default PowerPlantsBox;
