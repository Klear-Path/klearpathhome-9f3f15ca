import { Mail, MapPin } from "lucide-react";

const Footer = () => {
  return (
    <footer className="bg-slate-50 mt-20 pt-16 pb-8 border-t border-slate-200">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 mb-12 text-left">
          {/* Brand Column */}
          <div>
            <h3 className="text-xl font-bold mb-4 text-slate-900">KlearPath</h3>
            <p className="text-slate-600 max-w-xs">
              Advancing housing stability through specialized workforce training and comprehensive support systems.
            </p>
          </div>

          {/* Contact Column */}
          <div>
            <h4 className="font-semibold mb-4 text-slate-900">Contact Details</h4>
            <div className="space-y-4">
              <div className="flex items-start gap-3 text-slate-600">
                <MapPin className="w-5 h-5 mt-0.5 text-blue-600" />
                <p>410 Hopkins Ct<br />North Wales, PA 19454</p>
              </div>
              <div className="flex items-center gap-3 text-slate-600">
                <Mail className="w-5 h-5 text-blue-600" />
                <a href="mailto:info@klearpathhome.org" className="hover:text-blue-700 transition-colors underline">
                  info@klearpathhome.org
                </a>
              </div>
            </div>
          </div>

          {/* Legal Column - This is what Google looks for */}
          <div>
            <h4 className="font-semibold mb-4 text-slate-900">Compliance</h4>
            <div className="space-y-2">
              <p className="text-sm text-slate-600">EIN: 41-3156622</p>
              <p className="text-sm text-slate-600 italic">Registered 501(c)(3) Nonprofit</p>
              <div className="mt-6">
                <a 
                  href="/privacy.html" 
                  className="inline-block bg-white border border-slate-300 px-4 py-2 rounded-md text-sm font-medium text-slate-700 hover:bg-slate-100 hover:border-blue-500 transition-all shadow-sm"
                >
                  View Privacy Policy
                </a>
              </div>
            </div>
          </div>
        </div>

        <div className="border-t border-slate-200 pt-8 text-center text-sm text-slate-500">
          <p>&copy; {new Date().getFullYear()} KlearPath. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
