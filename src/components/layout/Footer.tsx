import { Link } from "react-router-dom";
import { Mail, Phone, MapPin } from "lucide-react";

const quickLinks = [
  { name: "The Model", href: "/model" },
  { name: "Counties & Partners", href: "/partners" },
  { name: "Impact & Accountability", href: "/impact" },
  { name: "Get Involved", href: "/get-involved" },
];

const legalLinks = [
  { name: "About Us", href: "/about" },
  { name: "Contact", href: "/contact" },
  { name: "Donate", href: "/donate" },
];

export function Footer() {
  return (
    <footer className="bg-primary text-primary-foreground">
      <div className="container-wide section-padding py-12 lg:py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12">
          {/* Brand */}
          <div className="lg:col-span-1">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 rounded-full bg-primary-foreground flex items-center justify-center">
                <span className="text-primary font-serif font-bold text-xl">K</span>
              </div>
              <span className="font-serif font-semibold text-xl">Klear Path</span>
            </Link>
            <p className="text-primary-foreground/80 text-sm leading-relaxed mb-4">
              Building pathways from crisis to stability for our neighbors in Bucks and Montgomery Counties, Pennsylvania.
            </p>
            <p className="text-primary-foreground/60 text-xs">
              Klear Path Home, Inc.<br />
              EIN: 41-3156622<br />
              501(c)(3) Nonprofit Organization
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="font-serif font-semibold text-lg mb-4">Quick Links</h3>
            <ul className="space-y-2">
              {quickLinks.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.href}
                    className="text-primary-foreground/80 hover:text-primary-foreground text-sm transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Organization */}
          <div>
            <h3 className="font-serif font-semibold text-lg mb-4">Organization</h3>
            <ul className="space-y-2">
              {legalLinks.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.href}
                    className="text-primary-foreground/80 hover:text-primary-foreground text-sm transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="font-serif font-semibold text-lg mb-4">Contact Us</h3>
            <ul className="space-y-3">
              <li className="flex items-start gap-2 text-sm">
                <MapPin className="w-4 h-4 mt-0.5 text-primary-foreground/60 flex-shrink-0" />
                <span className="text-primary-foreground/80">
                  Serving Bucks & Montgomery Counties, Pennsylvania
                </span>
              </li>
              <li className="flex items-center gap-2 text-sm">
                <Mail className="w-4 h-4 text-primary-foreground/60 flex-shrink-0" />
                <a
                  href="mailto:info@klearpathhome.org"
                  className="text-primary-foreground/80 hover:text-primary-foreground transition-colors"
                >
                  info@klearpathhome.org
                </a>
              </li>
              <li className="flex items-center gap-2 text-sm">
                <Phone className="w-4 h-4 text-primary-foreground/60 flex-shrink-0" />
                <a
                  href="tel:+12155551234"
                  className="text-primary-foreground/80 hover:text-primary-foreground transition-colors"
                >
                  (215) 555-1234
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-primary-foreground/20 mt-10 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-primary-foreground/60">
            <p>© {new Date().getFullYear()} Klear Path Home, Inc. All rights reserved.</p>
            <p>
              Domains: klearpathhome.org • klearpathhome.com
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
