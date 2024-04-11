import { useState } from "react";
import Uranium from "../../assets/uranium.png";
import Oil from "../../assets/oil.png";
import Gas from "../../assets/gas.png";
import Coal from "../../assets/coal.png";
import Biomass from "../../assets/corn.png";
import Electricity from "../../assets/electricity.png";

const Resources = [
  {
    name: "Electricity",
    image: Electricity,
    type: "ELECTRICITY",
    key: "max_energy_price",
  },
  { name: "Biomass", image: Biomass, type: "BIOMASS", key: "biomass" },
  { name: "Coal", image: Coal, type: "COAL", key: "coal" },
  { name: "Gas", image: Gas, type: "GAS", key: "gas" },
  { name: "Oil", image: Oil, type: "OIL", key: "oil" },
  { name: "Uranium", image: Uranium, type: "URANIUM", key: "uranium" },
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
      <img src={image} alt={resource.type} width={50} height={50} />
    </button>
  );
};

const SelectResourceBar = ({ selectedResource, setSelectedResource }) => {
  return (
    <div className="flex justify-between">
      {Resources.map((item) => (
        <SelectResourceButton
          key={item.name}
          resource={item}
          active={selectedResource.type == item.type ? true : false}
          setSelectedResource={setSelectedResource}
          image={item.image}
        />
      ))}
    </div>
  );
};

export default SelectResourceBar;
