const StatusBarItem = ({ ammount, unit }) => {
  return (
    <div className="flex justify-center align-center">
      <p>
        {ammount}&nbsp;{unit}
      </p>
    </div>
  );
};

export default StatusBarItem;
