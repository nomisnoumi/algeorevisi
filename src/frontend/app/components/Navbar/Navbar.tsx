"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import "./Navbar.css";

interface NavbarProps {
  theme?: "dark" | "light";
}

const Navbar = ({ theme = "dark" }) => {
  const pathname = usePathname();
  const links = [
    { href: "/searchcover", label: "search by cover" },
    { href: "/musicgallery", label: "music gallery" },
    { 
      href: "/searchsound", 
      label: "search by sound", 
      activePaths: ["/searchsound", "/soundresult"] // Add multiple active paths here
    },
  ];

  return (
    <nav className={`navbar ${theme === "dark" ? "nav-dark" : "nav-light"}`}>
      <ul className="navbar-links">
        {links.map((link) => {
          const isActive = link.activePaths
            ? link.activePaths.includes(pathname)
            : pathname === link.href;
          return (
            <li key={link.href} className={isActive ? "active" : ""}>
              <Link href={link.href}>{link.label}</Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
};

export default Navbar;
