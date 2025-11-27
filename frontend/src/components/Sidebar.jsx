import React from "react";
import styled from "styled-components";
import {
  MdDashboard,
  MdReport,
  MdSettings,
  MdSupport,
  MdExitToApp,
  MdHistory,
} from "react-icons/md";

// --- Styled Components ---
const NavContainer = styled.nav`
  width: 250px;
  background-color: #161b22; /* Slightly lighter dark color */
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-right: 1px solid #30363d;
`;

const SidebarHeader = styled.div`
  color: #3f9efc; /* Primary color for logo */
  font-size: 24px;
  font-weight: bold;
  padding: 0 20px 30px;
`;

const NavItem = styled.div`
  display: flex;
  align-items: center;
  padding: 15px 20px;
  cursor: pointer;
  background-color: ${(props) => (props.active ? "#1f6feb33" : "transparent")};
  color: ${(props) => (props.active ? "#58a6ff" : "#c9d1d9")};
  border-left: 4px solid
    ${(props) => (props.active ? "#3f9efc" : "transparent")};
  margin-bottom: 5px;

  &:hover {
    background-color: #1f6feb1a;
  }

  svg {
    margin-right: 10px;
  }
`;

const NavSection = styled.div`
  margin-top: ${(props) => (props.bottom ? "auto" : "0")};
`;

// --- Component ---
const navItemsTop = [
  { name: "Dashboard", icon: MdDashboard },
  { name: "Reports", icon: MdReport },
  // 💥 NEW HISTORY ITEM HERE! 💥
  { name: "History", icon: MdHistory },
  { name: "Settings", icon: MdSettings },
];

const navItemsBottom = [
  { name: "Support", icon: MdSupport },
  { name: "Logout", icon: MdExitToApp },
];

export default function Sidebar({ activeNav, setActiveNav }) {
  return (
    <NavContainer>
      <NavSection>
        <SidebarHeader>FraudGuard</SidebarHeader>
        {navItemsTop.map((item) => (
          <NavItem
            key={item.name}
            active={activeNav === item.name}
            onClick={() => setActiveNav(item.name)}
          >
            <item.icon /> {item.name}
          </NavItem>
        ))}
      </NavSection>
      <NavSection bottom>
        {navItemsBottom.map((item) => (
          <NavItem
            key={item.name}
            active={activeNav === item.name}
            onClick={() => setActiveNav(item.name)}
          >
            <item.icon /> {item.name}
          </NavItem>
        ))}
      </NavSection>
    </NavContainer>
  );
}
