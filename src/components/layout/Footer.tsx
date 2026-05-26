import { Link } from "react-router-dom";
import { Mail, MapPin } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-[#052e16] text-white">
      <div className="container mx-auto px-4 py-12 lg:py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">

          <div className="lg:col-span-1">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center">
                <span className="text-[#052e16] font-serif font-bold text-xl">K</span>
              </div>
              <span className="font-serif font-semibold text-xl">Klear Path</span>
            </Link>
            <p className="text-white/80 text-sm mb-3">
              <strong className="text-white">Klear Path Home, Inc.</strong> is a federally
              recognized 501(c)(3) public charity building workforce-driven housing stability
              programs in Bucks &amp; Montgomery Counties, PA.
            </p>
            <p className="text-white/60 text-xs">EIN: 41-3156622</p>
          </div>

          <div>
            <h3 className="font-semibold text-lg mb-4">Explore</h3>
            <ul className="space-y-2 text-sm text-white/80">
              <li><Link to="/housing-stabilization-model" className="hover:text-white">Our Model</Link></li>
              <li><Link to="/for-counties" className="hover:text-white">For Counties</Link></li>
              <li><Link to="/land-partnerships" className="hover:text-white">Land Partnerships</Link></li>
              <li><Link to="/fund-a-pilot" className="hover:text-white">Fund a Pilot</Link></li>
              <li><Link to="/partners" className="hover:text-white">Partners</Link></li>
              <li><Link to="/impact" className="hover:text-white">Impact &amp; Accountability</Link></li>
              <li><Link to="/volunteer" className="hover:text-white">Volunteer</Link></li>
              <li><Link to="/donate" className="hover:text-white">Donate</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold text-lg mb-4">Contact</h3>
            <div className="space-y-3 text-sm text-white/80">
              <div className="flex items-start gap-2">
                <MapPin className="w-4 h-4 mt-1 flex-shrink-0" />
                <address className="not-italic">
                  Klear Path Home, Inc.<br />
                  410 Hopkins Ct<br />
                  North Wales, PA 19454
                </address>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4" />
                <a href="mailto:info@klearpathhome.org" className="underline">info@klearpathhome.org</a>
              </div>
              <div>
                <Link to="/contact" className="underline">Contact form</Link>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-lg mb-4">Compliance</h3>
            <ul className="space-y-2 text-sm text-white/80 mb-4">
              <li>Legal name: <span className="text-white">Klear Path Home, Inc.</span></li>
              <li>501(c)(3) public charity</li>
              <li>EIN: 41-3156622</li>
            </ul>
            <Link
              to="/privacy-policy"
              className="inline-block bg-white text-[#052e16] px-5 py-2 rounded-md font-bold text-sm hover:bg-white/90"
            >
              Privacy Policy
            </Link>
          </div>

        </div>
        <div className="border-t border-white/10 mt-10 pt-8 text-center text-xs text-white/50">
          <p>© {new Date().getFullYear()} Klear Path Home, Inc. · 501(c)(3) · EIN 41-3156622 · 410 Hopkins Ct, North Wales, PA 19454. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
