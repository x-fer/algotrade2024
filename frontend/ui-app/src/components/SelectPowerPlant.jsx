import React from "react";

const SelectPowerPlant = ({ type, active }) => {
  return (
    <button
      className={`bg-dark-gray hover:bg-gray text-white text-xl w-60 h-24 rounded-3xl ${
        active ? "border-2 border-red" : ""
      }`}
    >
      {type}
    </button>
  );
};

export default SelectPowerPlant;
