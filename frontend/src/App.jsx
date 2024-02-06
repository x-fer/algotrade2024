import './App.css'
import Home from './views/Home.jsx'
import { BrowserRouter, Route, Routes } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route exact path="/" Component={Home} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
