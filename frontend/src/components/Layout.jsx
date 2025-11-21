import React from 'react'
import Footer from './Footer';
import Header from './Header';
import { Outlet } from 'react-router-dom';
import AIChat from './chat/AIChat';

const Layout = () => {
  return (
    <div className="w-screen min-h-screen flex flex-col bg-white overflow-x-hidden">
      <Header/>
      
      <main className="flex-1">
        <Outlet />
      </main>

      <Footer/>
      <AIChat/>
    </div>
  )
}

export default Layout;
