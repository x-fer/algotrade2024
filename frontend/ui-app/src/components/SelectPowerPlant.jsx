import React from "react";

const SelectPowerPlant = ({ type, active, setSelectedType }) => {
  return (
    <button
      className={` hover:bg-dark-gray focus:bg-black text-white text-xl w-48 h-24 rounded-3xl ${
        active ? "border-2 border-red bg-black" : "bg-gray"
      }`}
      onClick={() => setSelectedType(type)}
    >
      {type}
    </button>
  );
};

export default SelectPowerPlant;
