import React, { useContext, useState } from "react";
import { useForm } from "react-hook-form";
import SelectResourceBar from "./SelectResourceBar";
import { DataContext } from "../DataProvider";
import BuySell from "./BuySell";
import EnergySell from "./EnergySell";

const OrderBox = () => {
  const { selectedResource, setSelectedResource } = useContext(DataContext);

  const { register, handleSubmit, setValue } = useForm();

  const onSubmit = (data) => {
    const order = {
      side: data.action,
      resource: selectedResource,
      size: data.size,
      price: data.price,
    };
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
        {selectedResource.type === "ELECTRICITY" ? (
          <EnergySell
            handleButtonClick={handleButtonClick}
            register={register}
          />
        ) : (
          <BuySell handleButtonClick={handleButtonClick} register={register} />
        )}
      </div>
    </form>
  );
};

export default OrderBox;
