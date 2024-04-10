import React, { useContext, useState } from "react";
import { useForm } from "react-hook-form";
import SelectResourceBar from "./SelectResourceBar";
import instance from "../../api/apiInstance";
import { DataContext } from "../DataProvider";
import BuySell from "./BuySell";
import EnergySell from "./EnergySell";

const OrderBox = () => {
  const { gameId, playerId, teamSecret } = useContext(DataContext);
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
      <div className="flex flex-col p-4 gap-8 rounded-3xl bg-primary">
        <SelectResourceBar
          selectedResource={selectedResource}
          setSelectedResource={setSelectedResource}
        />
        {selectedResource !== "ELECTRICITY" ? (
          <BuySell handleButtonClick={handleButtonClick} register={register} />
        ) : (
          <EnergySell
            handleButtonClick={handleButtonClick}
            register={register}
          />
        )}
      </div>
    </form>
  );
};

export default OrderBox;
