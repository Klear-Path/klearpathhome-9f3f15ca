import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Menu, X, LifeBuoy } from "lucide-react";
import { Button } from "@/components/ui/button";

const navigation = [
  { name: "Home", href: "/" },
  { name: "Our Model", href: "/housing-stabilization-model" },
  { name: "For Counties", href: "/for-counties" },
  { name: "Land Partnerships", href: "/land-partnerships" },
  { name: "Fund a Pilot", href: "/fund-a-pilot" },
  { name: "About", href: "/about" },
  { name: "Contact", href: "/contact" },
];

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  return (
    <header className="sticky top-0 z-50 bg-card/95 backdrop-blur-sm border-b border-border">
      <nav className="container-wide section-padding" aria-label="Main navigation">
        <div className="flex h-16 items-center justify-between lg:h-20">
          <Link to="/" className="flex items-center gap-2" aria-label="Klear Path Home">
            <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-serif font-bold text-xl">K</span>
            </div>
            <span className="font-serif font-semibold text-xl text-foreground">Klear Path</span>
          </Link>

          <div className="hidden xl:flex xl:items-center xl:gap-1">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  location.pathname === item.href
                    ? "text-primary bg-accent"
                    : "text-muted-foreground hover:text-foreground hover:bg-secondary"
                }`}
              >
                {item.name}
              </Link>
            ))}
            <Link to="/get-help" className="ml-2" data-cta="nav-get-help">
              <Button variant="outline" size="sm">
                <LifeBuoy className="h-4 w-4" aria-hidden="true" />
                Get Help
              </Button>
            </Link>
            <Link to="/donate" className="ml-2" data-cta="nav-donate">
              <Button variant="default" size="sm">
                Donate
              </Button>
            </Link>
          </div>

          <button
            type="button"
            className="xl:hidden p-2 rounded-md text-foreground"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-expanded={mobileMenuOpen}
            aria-controls="mobile-menu"
          >
            <span className="sr-only">Toggle menu</span>
            {mobileMenuOpen ? <X className="h-6 w-6" aria-hidden="true" /> : <Menu className="h-6 w-6" aria-hidden="true" />}
          </button>
        </div>

        {mobileMenuOpen && (
          <div id="mobile-menu" className="xl:hidden pb-4 animate-fade-in">
            <div className="flex flex-col gap-1">
              <Link
                to="/get-help"
                onClick={() => setMobileMenuOpen(false)}
                className="mb-2"
                data-cta="mobile-menu-get-help"
              >
                <Button variant="outline" className="w-full">
                  <LifeBuoy className="h-4 w-4" aria-hidden="true" />
                  Get Help
                </Button>
              </Link>
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`px-4 py-3 text-base font-medium rounded-md transition-colors ${
                    location.pathname === item.href
                      ? "text-primary bg-accent"
                      : "text-muted-foreground hover:text-foreground hover:bg-secondary"
                  }`}
                >
                  {item.name}
                </Link>
              ))}
              <Link to="/donate" onClick={() => setMobileMenuOpen(false)} className="mt-2" data-cta="mobile-menu-donate">
                <Button variant="default" className="w-full">
                  Donate
                </Button>
              </Link>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
}
