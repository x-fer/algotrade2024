import StatusBarItem from "./StatusBarItem";

const StatusBar = () => {
  return (
    <div className="flex justify-around w-full bg-blue-200">
      <StatusBarItem ammount={100} unit="€" />
      <StatusBarItem ammount={100} unit="biomass" />
      <StatusBarItem ammount={100} unit="coal" />
      <StatusBarItem ammount={100} unit="gas" />
      <StatusBarItem ammount={100} unit="oil" />
      <StatusBarItem ammount={100} unit="uranium" />
    </div>
  );
};

export default StatusBar;
