import React from "react";

import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const data = [
  { name: "Jan", uv: 20 },
  { name: "Feb", uv: 25 },
  { name: "Mar", uv: 40 },
  { name: "Apr", uv: 52 },
  { name: "May", uv: 70 },
  { name: "Jun", uv: 86 },
  { name: "Jul", uv: 110 },
  { name: "Aug", uv: 105 },
  { name: "Sep", uv: 70 },
  { name: "Oct", uv: 40 },
  { name: "Nov", uv: 32 },
  { name: "Dec", uv: 17 },
];

const RenderLineChart = () => (
  <ResponsiveContainer width="100%" height="100%">
    <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
      <Line type="basic" dataKey="uv" stroke="#dd4734" strokeWidth={3} />
      <CartesianGrid stroke="#7d373e" strokeDasharray="6 6" />
      <XAxis dataKey="name" />
      <YAxis />
      <Tooltip />
    </LineChart>
  </ResponsiveContainer>
);

const PriceChart = () => {
  return (
    <div className="w-[50vw] h-[50vh] rounded-3xl bg-black p-8">
      <RenderLineChart />
    </div>
  );
};

export default PriceChart;
