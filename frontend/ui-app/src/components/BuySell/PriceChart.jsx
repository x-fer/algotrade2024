import React, { useContext } from "react";

import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Label,
} from "recharts";
import { DataContext } from "../DataProvider";

const RenderLineChart = ({ data }) => (
  <ResponsiveContainer width="100%" height="100%">
    <LineChart data={data} margin={{ top: 5, right: 20, bottom: 20, left: 20 }}>
      <Line
        type="monotone"
        dataKey="price"
        stroke="#dd4734"
        strokeWidth={2}
        dot={false}
      />
      <XAxis dataKey="tick">
        <Label value="Time" offset={0} position="bottom" />
      </XAxis>
      <YAxis>
        <Label value="Price" offset={0} angle={-90} position="insideLeft" />
      </YAxis>
      <Tooltip label={[{ hej: 2 }]} />
    </LineChart>
  </ResponsiveContainer>
);

const PriceChart = () => {
  const { graphData, selectedResource } = useContext(DataContext);
  let data;

  if (!selectedResource) {
  } else {
    if (selectedResource.type === "ELECTRICITY") {
      data = Object.values(graphData).map((item) => {
        return { tick: item["tick"], price: item["max_energy_price"] };
      });
    } else {
      data = Object.values(graphData).map((item) => {
        return {
          tick: item["tick"],
          price: item["resource_prices"][selectedResource.key],
        };
      });
    }
  }

  return (
    <div className="w-[42vw] h-[50vh] rounded-3xl bg-black p-8">
      <RenderLineChart data={data} />
    </div>
  );
};

export default PriceChart;
