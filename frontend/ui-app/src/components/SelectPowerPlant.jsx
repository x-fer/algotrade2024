import React from "react";

const SelectPowerPlant = ({ type, active, setSelectedType }) => {
  return (
    <button
      className={` hover:bg-tertiary focus:bg-tertiary text-white text-xl w-[10vw] h-full rounded-3xl ${
        active ? "border-2 border-red bg-tertiary" : "bg-secondary"
      }`}
      onClick={() => setSelectedType(type)}
    >
      {type}
    </button>
  );
};

export default SelectPowerPlant;
