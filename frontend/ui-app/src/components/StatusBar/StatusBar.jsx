import { useContext, useEffect, useState } from "react";
import StatusBarItem from "./StatusBarItem";
import { DataContext } from "../DataProvider";

const StatusBar = () => {
  const { playerData } = useContext(DataContext);

  return (
    <div className="flex justify-around p-4 rounded-3xl gap-6 bg-primary text-white shadow-xl">
      <StatusBarItem ammount={playerData.money} unit="€" />
      <StatusBarItem ammount={playerData.energy} unit="MW" />
      <StatusBarItem ammount={playerData.resources?.biomass} unit="biomass" />
      <StatusBarItem ammount={playerData.resources?.coal} unit="coal" />
      <StatusBarItem ammount={playerData.resources?.gas} unit="gas" />
      <StatusBarItem ammount={playerData.resources?.oil} unit="oil" />
      <StatusBarItem ammount={playerData.resources?.uranium} unit="uranium" />
    </div>
  );
};

export default StatusBar;
