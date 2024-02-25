import React from "react";

const SelectPowerPlant = ({ type, active, setSelectedType }) => {
  return (
    <button
      className={`bg-dark-gray hover:bg-gray text-white text-xl w-60 h-24 rounded-3xl ${
        active ? "border-2 border-red" : ""
      }`}
      onClick={() => setSelectedType(type)}
    >
      {type}
    </button>
  );
};

export default SelectPowerPlant;
