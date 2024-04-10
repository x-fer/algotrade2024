import { createContext, useState } from "react";

export const DataContext = createContext();

const DataProvider = ({children}) => {
    const [gameId, setGameId] = useState(0);
    const [playerId, setPlayerId] = useState(0);
    const [teamSecret, setTeamSecret] = useState("");

    return (
        <DataContext.Provider
            value={{
                gameId,
                setGameId,
                playerId,
                setPlayerId,
                teamSecret,
                setTeamSecret,
            }}
        >
            {children}
        </DataContext.Provider>
    );
};

export default DataProvider;
