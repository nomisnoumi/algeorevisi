"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import simsalabimlogo from "../../../public/simsalabimlogoblack.png";
import { usePathname } from "next/navigation";
import "./Top.css";

const Top = () => {
  const pathname = usePathname();

  return (
    <div className="top-container">
      <ul className="top-links-left">
        <li className={pathname === "/aboutus" ? "active" : ""}>
          <Link href="/aboutus">about us</Link>
        </li>
      </ul>

      <div className="logo-container">
        <Link href="/">
          <Image
            src={simsalabimlogo}
            alt="Simsalabim Logo"
            width={200}
            height={200}
            priority
          />
        </Link>
      </div>

      <ul className="top-links-right">
        <li className={pathname === "/howtouse" ? "active" : ""}>
          <Link href="/howtouse">how to use</Link>
        </li>
      </ul>
    </div>
  );
};

export default Top;