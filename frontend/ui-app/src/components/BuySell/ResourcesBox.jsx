import OrderBox from "./OrderBox";
import PriceChart from "./PriceChart";

const ResourcesBox = () => {
  return (
    <div className="flex flex-col justify-between gap-4 p-4 rounded-3xl bg-primary">
      <OrderBox />

      <PriceChart />
    </div>
  );
};

export default ResourcesBox;
