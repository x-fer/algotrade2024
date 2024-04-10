import { useState } from "react";
import Uranium from "../../assets/uranium.png";
import Oil from "../../assets/oil.png";
import Gas from "../../assets/gas.png";
import Coal from "../../assets/coal.png";
import Biomass from "../../assets/corn.png";
import Electricity from "../../assets/electricity.png";

const Resources = [
  { name: "Electricity", image: Electricity, type: "ELECTRICITY" },
  { name: "Biomass", image: Biomass, type: "BIOMASS" },
  { name: "Coal", image: Coal, type: "COAL" },
  { name: "Gas", image: Gas, type: "GAS" },
  { name: "Oil", image: Oil, type: "OIL" },
  { name: "Uranium", image: Uranium, type: "URANIUM" },
];

const SelectResourceButton = ({
  resource,
  active,
  image,
  setSelectedResource,
}) => {
  return (
    <button
      className={`bg-tertiary  hover:bg-seconday border-[3px] text-white text-xl p-4 rounded-3xl  ${
        active ? "border-red" : "border-tertiary"
      }`}
      type="button"
      onClick={() => setSelectedResource(resource)}
    >
      <img src={image} alt={resource} width={50} height={50} />
    </button>
  );
};

const SelectResourceBar = ({ selectedResource, setSelectedResource }) => {
  return (
    <div className="flex justify-between">
      {Resources.map((item) => (
        <SelectResourceButton
          key={item.name}
          resource={item.type}
          active={selectedResource == item.type ? true : false}
          setSelectedResource={setSelectedResource}
          image={item.image}
        />
      ))}
    </div>
  );
};

export default SelectResourceBar;
