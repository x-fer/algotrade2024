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
    key: "electricity",
  },
  { name: "Biomass", image: Biomass, key: "biomass" },
  { name: "Coal", image: Coal, key: "coal" },
  { name: "Gas", image: Gas, key: "gas" },
  { name: "Oil", image: Oil, key: "oil" },
  { name: "Uranium", image: Uranium, key: "uranium" },
];

const SelectResourceButton = ({
  resource,
  active,
  image,
  setSelectedResource,
}) => {
  return (
    <button
      className={`bg-tertiary  hover:bg-seconday border-[2px] text-white text-xl p-2 rounded-3xl  ${
        active ? "border-white" : "border-tertiary"
      }`}
      type="button"
      onClick={() => setSelectedResource(resource)}
    >
      <img src={image} alt={resource.key} width={50} height={50} />
    </button>
  );
};

const SelectResourceBar = ({ selectedResource, setSelectedResource }) => {
  return (
    <div className="flex justify-around">
      {Resources.map((item) => (
        <SelectResourceButton
          key={item.name}
          resource={item}
          active={selectedResource?.key == item.key ? true : false}
          setSelectedResource={setSelectedResource}
          image={item.image}
        />
      ))}
    </div>
  );
};

export default SelectResourceBar;
