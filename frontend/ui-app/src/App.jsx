import React, {useState} from 'react'
import './App.css'
import LeftBar from './components/LeftBar'
import MiddleScreen from './components/MiddleScreen'
import RightBar from './components/RightBar'

const App = () => {
  const [count, setCount] = useState(0)

  return (
    <div className='flex'>
      <LeftBar/>
      <MiddleScreen/>
      <RightBar/>
    </div>  )
}

export default App
