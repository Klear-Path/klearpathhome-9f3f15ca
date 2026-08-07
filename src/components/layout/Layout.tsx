import { ReactNode } from "react";
import { useLocation } from "react-router-dom";
import { Header } from "./Header";
import { Footer } from "./Footer";
import { FloatingDonateButton } from "@/components/FloatingDonateButton";
import { FloatingCallButton } from "@/components/FloatingCallButton";

interface LayoutProps {
  children: ReactNode;
}

/** Pages written for people seeking help, where the mobile bar should offer a
 *  phone call rather than a donation prompt. */
const HELP_SEEKER_ROUTES = ["/get-help"];

export function Layout({ children }: LayoutProps) {
  const { pathname } = useLocation();
  const isHelpSeekerRoute = HELP_SEEKER_ROUTES.includes(pathname);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">{children}</main>
      <Footer />
      {isHelpSeekerRoute ? <FloatingCallButton /> : <FloatingDonateButton />}
    </div>
  );
}
