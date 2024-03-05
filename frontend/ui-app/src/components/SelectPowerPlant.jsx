import React from "react";

const SelectPowerPlant = ({ type, active, setSelectedType }) => {
  return (
    <button
      className={` hover:bg-tertiary active:bg-primary border-[3px]  text-white text-xl w-[10vw] h-full rounded-3xl ${
        active ? " border-red bg-tertiary" : "bg-secondary border-secondary"
      }`}
      onClick={() => setSelectedType(type)}
    >
      {type}
    </button>
  );
};

export default SelectPowerPlant;
