const StatusBarItem = ({ ammount, unit }) => {
  return (
    <div className="flex flex-col text-xl justify-center justify-items-center h-40">
      {ammount}&nbsp;{unit}
    </div>
  );
};

export default StatusBarItem;
