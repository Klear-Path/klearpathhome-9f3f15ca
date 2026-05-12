import { Link } from "react-router-dom";
import { Mail, MapPin } from "lucide-react";

export function Footer() {
  const quickLinks = [
    { name: "Our Model", href: "/housing-stabilization-model" },
    { name: "For Counties", href: "/for-counties" },
    { name: "Land Partnerships", href: "/land-partnerships" },
    { name: "Fund a Pilot", href: "/fund-a-pilot" },
  ];

  const orgLinks = [
    { name: "About Us", href: "/about" },
    { name: "Contact", href: "/contact" },
    { name: "Donate", href: "/donate" },
    { name: "Partners", href: "/partners" },
  ];

  return (
    <footer className="bg-[#052e16] text-white">
      <div className="container-wide section-padding py-12 lg:py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12">
          
          <div className="lg:col-span-1">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center">
                <span className="text-[#052e16] font-serif font-bold text-xl">K</span>
              </div>
              <span className="font-serif font-semibold text-xl">Klear Path</span>
            </Link>
            <p className="text-white/80 text-sm leading-relaxed mb-4">
              A 501(c)(3) nonprofit building workforce-driven housing stability programs.
            </p>
            <p className="text-white/60 text-xs font-mono">
              EIN: 41-3156622
            </p>
          </div>

          <div>
            <h3 className="font-serif font-semibold text-lg mb-4 text-white">Quick Links</h3>
            <ul className="space-y-2">
              {quickLinks.map((link) => (
                <li key={link.name}>
                  <Link to={link.href} className="text-white/80 hover:text-white text-sm transition-colors">
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="font-serif font-semibold text-lg mb-4 text-white">Contact Us</h3>
            <div className="space-y-3 text-sm text-white/80">
              <div className="flex items-start gap-2">
                <MapPin className="w-4 h-4 mt-1 text-white/60" />
                <span>410 Hopkins Ct<br />North Wales, PA 19454</span>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4 text-white/60" />
                <a href="mailto:info@klearpathhome.org" className="hover:text-white underline transition-colors">
                  info@klearpathhome.org
                </a>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-serif font-semibold text-lg mb-4 text-white">Compliance</h3>
            <p className="text-sm text-white/70 mb-4 italic">Registered 501(c)(3) Nonprofit</p>
            <a 
              href="/privacy.html" 
              className="inline-block bg-white text-[#052e16] px-6 py-2 rounded-md font-bold hover:bg-gray-100 transition-all shadow-sm text-sm"
            >
              Privacy Policy
            </a>
          </div>

        </div>

        <div className="border-t border-white/10 mt-10 pt-8 text-center text-xs text-white/40">
          <p>© {new Date().getFullYear()} Klear Path Home, Inc. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
