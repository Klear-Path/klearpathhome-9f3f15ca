import { Phone } from "lucide-react";
import { PRIMARY_PHONE } from "@/lib/site";

/**
 * Mobile counterpart to FloatingDonateButton, for pages aimed at people who
 * need help rather than people who might give it. Asking someone who just lost
 * their ID to donate is the wrong ask; a tap-to-call is the right one.
 */
export function FloatingCallButton() {
  return (
    <a
      href={`tel:${PRIMARY_PHONE.href}`}
      data-cta="mobile-floating-call"
      className="fixed bottom-4 left-4 right-4 z-50 md:hidden"
    >
      <div className="bg-primary text-primary-foreground rounded-full shadow-2xl px-5 py-4 flex items-center justify-center gap-2 font-semibold text-sm">
        <Phone className="w-4 h-4" aria-hidden="true" />
        Call {PRIMARY_PHONE.display}
      </div>
    </a>
  );
}
