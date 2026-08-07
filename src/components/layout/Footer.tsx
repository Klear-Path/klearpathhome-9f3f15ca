import { Link } from "react-router-dom";
import { Mail, MapPin, Phone } from "lucide-react";
import { PHONES, PRIMARY_PHONE, SITE } from "@/lib/site";

export function Footer() {
  return (
    <footer className="bg-[#052e16] text-white">
      {/* Extra bottom padding on mobile clears the fixed floating action bar,
          which would otherwise sit on top of the copyright line. */}
      <div className="container mx-auto px-4 py-12 lg:py-16 pb-28 md:pb-12 lg:pb-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">

          <div className="lg:col-span-1">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center">
                <span className="text-[#052e16] font-serif font-bold text-xl">K</span>
              </div>
              <span className="font-serif font-semibold text-xl">Klear Path</span>
            </Link>
            <p className="text-white/80 text-sm mb-3">
              <strong className="text-white">{SITE.legalName}</strong> is a federally
              recognized 501(c)(3) public charity building workforce-driven housing stability
              programs in Bucks &amp; Montgomery Counties, PA.
            </p>
            <p className="text-white/60 text-xs">EIN: {SITE.ein}</p>
          </div>

          <div>
            <h3 className="font-semibold text-lg mb-4">Explore</h3>
            <ul className="space-y-2 text-sm text-white/80">
              <li><Link to="/get-help" className="font-semibold text-white hover:underline">Get Help With Documents</Link></li>
              <li><Link to="/housing-stabilization-model" className="hover:text-white">Our Model</Link></li>
              <li><Link to="/dignity-first-model" className="hover:text-white">Dignity-First Model</Link></li>
              <li><Link to="/for-counties" className="hover:text-white">For Counties</Link></li>
              <li><Link to="/land-partnerships" className="hover:text-white">Land Partnerships</Link></li>
              <li><Link to="/fund-a-pilot" className="hover:text-white">Fund a Pilot</Link></li>
              <li><Link to="/veterans" className="hover:text-white">Support Veterans</Link></li>
              <li><Link to="/corporate-sponsors" className="hover:text-white">Corporate Sponsors</Link></li>
              <li><Link to="/employer-partners" className="hover:text-white">Employer Partners</Link></li>
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
                  {SITE.legalName}<br />
                  {SITE.address.street}<br />
                  {SITE.address.city}, {SITE.address.state} {SITE.address.zip}
                </address>
              </div>
              <div className="flex items-start gap-2">
                <Phone className="w-4 h-4 mt-1 flex-shrink-0" />
                <div>
                  {PHONES.map((phone) => (
                    <a key={phone.href} href={`tel:${phone.href}`} className="block underline">
                      {phone.display}
                    </a>
                  ))}
                  <p className="text-xs text-white/60 mt-1">{SITE.officeHours}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4" />
                <a href={`mailto:${SITE.email}`} className="underline">{SITE.email}</a>
              </div>
              <p className="text-xs text-white/60 mt-2">
                Service focus: {SITE.serviceArea}.
              </p>
              <div>
                <Link to="/contact" className="underline">Contact form</Link>
              </div>
              <div className="rounded-lg bg-white/10 p-3 mt-3">
                <p className="text-white font-semibold text-sm">Need a document replaced?</p>
                <p className="text-white/80 text-xs mt-1">
                  We cover the fee for a birth certificate, state ID, Social Security card,
                  or DD-214.
                </p>
                <Link to="/get-help" className="inline-block text-white underline text-sm mt-2">
                  Get help
                </Link>{" "}
                <span className="text-white/60 text-sm">or call</span>{" "}
                <a href={`tel:${PRIMARY_PHONE.href}`} className="text-white underline text-sm">
                  {PRIMARY_PHONE.display}
                </a>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-lg mb-4">Compliance</h3>
            <ul className="space-y-2 text-sm text-white/80 mb-4">
              <li>Legal name: <span className="text-white">{SITE.legalName}</span></li>
              <li>501(c)(3) public charity</li>
              <li>EIN: {SITE.ein}</li>
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
          <p>© {new Date().getFullYear()} {SITE.legalName} · 501(c)(3) nonprofit · EIN {SITE.ein} · {SITE.address.street}, {SITE.address.city}, {SITE.address.state} {SITE.address.zip} · Serving {SITE.serviceArea}. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
