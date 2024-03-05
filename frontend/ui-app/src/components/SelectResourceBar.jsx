import { useState } from "react";
import Uranium from "../assets/uranium.png";
import Oil from "../assets/oil.png";
import Gas from "../assets/gas.png";
import Coal from "../assets/coal.png";
import Biomass from "../assets/corn.png";

const Resources = [
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
      className={`bg-tertiary  hover:bg-seconday border-[3px] text-white text-xl p-2 rounded-3xl mx-0.5  ${
        active ? "border-red" : "border-tertiary"
      }`}
      type="button"
      onClick={() => setSelectedResource(resource)}
    >
      <img src={image} alt={resource} width={40} height={40} />
    </button>
  );
};

const SelectResourceBar = ({ selectedResource, setSelectedResource }) => {
  return (
    <div className="flex justify-around">
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
