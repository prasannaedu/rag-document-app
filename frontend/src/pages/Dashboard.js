import React from 'react';
import Upload from '../components/Upload';
import Query from '../components/Query';

const Dashboard = () => {
  return (
    <div>
      <h1>RAG Document Dashboard</h1>
      <Upload />
      <Query />
    </div>
  );
};

export default Dashboard;
