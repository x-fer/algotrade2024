import { useState } from "react";
import SelectFuelButton from "./SelectFuelButton";
import Uranium from "../assets/uranium.png";
import Oil from "../assets/oil.png";
import Gas from "../assets/gas.png";
import Coal from "../assets/coal.png";
import Biomass from "../assets/corn.png";

const FuelTypes = [
  { type: "Biomass", image: Biomass },
  { type: "Coal", image: Coal },
  { type: "Gas", image: Gas },
  { type: "Oil", image: Oil },
  { type: "Uranium", image: Uranium },
];

const SelectFuelBar = () => {
  const [selectedFuel, setSelectedFuel] = useState("");

  return (
    <div className="flex bg-black-gray justify-around mt-4">
      {FuelTypes.map((item) => (
        <SelectFuelButton
          key={item.type}
          type={item.type}
          active={selectedFuel == item.type ? true : false}
          setSelectedFuel={setSelectedFuel}
          image={item.image}
        />
      ))}
    </div>
  );
};

export default SelectFuelBar;
