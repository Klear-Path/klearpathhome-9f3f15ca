import { Heart } from "lucide-react";
import { Link } from "react-router-dom";

export function FloatingDonateButton() {
  return (
    <Link
      to="/donate"
      data-cta="mobile-floating-donate"
      className="fixed bottom-4 left-4 right-4 z-50 md:hidden"
    >
      <div className="bg-primary text-primary-foreground rounded-full shadow-2xl px-5 py-4 flex items-center justify-center gap-2 font-semibold text-sm">
        <Heart className="w-4 h-4" />
        Help Someone Today
      </div>
    </Link>
  );
}
