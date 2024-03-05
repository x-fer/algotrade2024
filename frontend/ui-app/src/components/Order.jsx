import React, { useContext, useState } from "react";
import { useForm } from "react-hook-form";
import SelectResourceBar from "./SelectResourceBar";
import instance from "../api/apiInstance";
import { Context } from "../Context";

const Order = () => {
  const { gameId, playerId, teamSecret } = useContext(Context);
  const [selectedResource, setSelectedResource] = useState("");

  const { register, handleSubmit, setValue } = useForm();

  const onSubmit = (data) => {
    const order = {
      side: data.action,
      resource: selectedResource,
      size: data.size,
      price: data.price,
    };

    instance
      .post(`/game/${gameId}/player/${playerId}/orders/create`, order, {
        params: { team_secret: teamSecret },
      })
      .then((response) => {
        console.log(response);
      });
  };

  const handleButtonClick = (action) => {
    setValue("action", action);
    handleSubmit(onSubmit)();
  };

  return (
    <form className="text-white">
      <div className="flex flex-col my-2 mt-4 p-4 rounded-3xl bg-primary">
        <SelectResourceBar
          selectedResource={selectedResource}
          setSelectedResource={setSelectedResource}
        />

        <div className="flex justify-between items-center mt-8">
          <div>
            <label className="font-l">Quantity:</label>
            <input
              className="bg-secondary  p-2 rounded-2xl w-16 ml-2"
              type="number"
              id="size"
              name="size"
              {...register("size", { required: true, min: 1 })}
            />
          </div>

          <div>
            <label className="font-l">Price:</label>
            <input
              className="bg-secondary  p-2 rounded-2xl w-16 ml-2"
              type="number"
              id="price"
              name="price"
              {...register("price", { required: true, min: 1 })}
            />
          </div>
        </div>

        <div className="flex justify-around mt-8">
          <div className="flex justify-around font-bold">
            <button
              className="bg-green py-2 px-4 rounded-2xl"
              type="button"
              onClick={() => handleButtonClick("buy")}
            >
              BUY
            </button>
          </div>

          <div className="flex justify-around font-bold">
            <button
              className="bg-red py-2 px-4 rounded-2xl"
              type="button"
              onClick={() => handleButtonClick("sell")}
            >
              SELL
            </button>
          </div>
        </div>
      </div>
    </form>
  );
};

export default Order;
