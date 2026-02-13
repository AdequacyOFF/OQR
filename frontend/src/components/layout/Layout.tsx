import React from 'react';
import Header from './Header';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <>
      <Header />
      <main className="main-content">
        <div className="container">{children}</div>
      </main>
    </>
  );
};

export default Layout;
