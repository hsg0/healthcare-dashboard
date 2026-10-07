// WHAT — Starts the React app in the browser.
// WHY — index.html has an empty div. This file fills it.
// HOW — It finds the div with id "root" and renders App inside it.
// IMPORTANT — Keep this file small. Screen content belongs in App and the pages added later.

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
