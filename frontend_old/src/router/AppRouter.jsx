import React from 'react';
import Layout from '../components/Layout';
import { Route, Routes } from 'react-router-dom';
import { ROUTES } from './routes/routeConfig';
import HomePage from '../pages/Home';

const AppRouter = () => {
  return (
    <Routes>

      <Route element={<Layout />}>

        {/* Home Page */}
        <Route path={ROUTES.HOME} element={<HomePage />} />

      </Route>

    </Routes>
  );
};

export default AppRouter;
