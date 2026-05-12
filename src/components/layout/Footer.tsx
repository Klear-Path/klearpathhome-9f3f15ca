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
            <p className="text-white/80 text-sm mb-4">
              A 501(c)(3) nonprofit building workforce-driven housing stability programs.
            </p>
          </div>

          <div>
            <h3 className="font-semibold text-lg mb-4">Contact</h3>
            <div className="space-y-3 text-sm text-white/80">
              <div className="flex items-start gap-2">
                <MapPin className="w-4 h-4 mt-1" />
                <span>410 Hopkins Ct, North Wales, PA 19454</span>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4" />
                <a href="mailto:info@klearpathhome.org" className="underline">info@klearpathhome.org</a>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-lg mb-4">Compliance</h3>
            <p className="text-sm text-white/70 mb-4">EIN: 41-3156622</p>
            <a 
              href="/privacy.html" 
              className="inline-block bg-white text-[#052e16] px-6 py-2 rounded-md font-bold text-sm"
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
