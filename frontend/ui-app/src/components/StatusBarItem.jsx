const StatusBarItem = ({ ammount, unit }) => {
  return (
    <div className="flex flex-col justify-center justify-items-center rounded-3xl h-[10vh] w-full bg-secondary text-xl">
      {ammount}&nbsp;{unit}
    </div>
  );
};

export default StatusBarItem;
