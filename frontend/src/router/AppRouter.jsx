import React from 'react'
import Layout from '../components/Layout';
import { Route, Routes } from 'react-router-dom';
import { ROUTES } from './routes/routeConfig';
import HomePage from '../pages/Home';

const AppRouter = () => {
  return (
    <div>
      <Layout>
        <Routes>
          <Route
          path = {ROUTES.HOME}
          element = {<HomePage/>}/>
        </Routes>
      </Layout>
    </div> 
  )
}

export default AppRouter;
