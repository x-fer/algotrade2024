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
  <ResponsiveContainer>
    <LineChart data={data} margin={{ top: 0, right: 5, bottom: 14, left: 10 }}>
      <Line
        type="monotone"
        dataKey="price"
        stroke="#dd4734"
        strokeWidth={2}
        dot={false}
      />
      <XAxis dataKey="tick">
        <Label value="Tick" offset={0} position="bottom" />
      </XAxis>
      <YAxis>
        <Label value="Price" offset={0} angle={-90} position="insideLeft" />
      </YAxis>
      <Tooltip />
    </LineChart>
  </ResponsiveContainer>
);

const PriceChart = () => {
  const { graphData, selectedResource } = useContext(DataContext);
  let data;

  if (!selectedResource) {
  } else {
    if (selectedResource.key === "electricity") {
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
    <div className="w-[42vw] h-[50vh] rounded-3xl p-8">
      <RenderLineChart data={data} />
    </div>
  );
};

export default PriceChart;
