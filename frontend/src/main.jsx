import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import '@sebgroup/fonts/css/seb-fonts.css'
import '@sebgroup/chlorophyll/css/green-chlorophyll.css'
import './index.css'

import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)