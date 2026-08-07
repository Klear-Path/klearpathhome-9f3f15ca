/**
 * Single source of truth for organization details that appear in more than one
 * place. Phone numbers, the EIN, and the mailing address were previously copied
 * across pages, the footer, and the JSON-LD block in index.html, which is how
 * they drift apart. Import from here instead of retyping them.
 */

export const SITE = {
  legalName: "Klear Path Home, Inc.",
  shortName: "Klear Path",
  ein: "41-3156622",
  url: "https://klearpathhome.org",
  email: "erickmckee@klearpathhome.org",
  address: {
    street: "410 Hopkins Ct",
    city: "North Wales",
    state: "PA",
    zip: "19454",
  },
  serviceArea:
    "Montgomery County, Bucks County, and the Pottstown regional service area",
  officeHours: "Monday – Friday, 9am – 5pm ET",
} as const;

export type Phone = {
  /** How the number is shown to a reader. */
  display: string;
  /** E.164 form for the `tel:` href. */
  href: string;
  label: string;
};

export const PHONES: readonly Phone[] = [
  { display: "(215) 986-7246", href: "+12159867246", label: "Main" },
  { display: "(844) 455-8883", href: "+18444558883", label: "Toll-free" },
] as const;

/** The number to lead with on calls-to-action. */
export const PRIMARY_PHONE = PHONES[0];

/**
 * Google Ads conversion actions. The global Ads tag (AW-18192459416) is already
 * loaded in index.html; these are the per-action `send_to` values. Create the
 * conversion action in Google Ads, paste its "AW-XXXXXXXXX/label" string here,
 * and tracking starts working. Everything degrades quietly while they are null.
 */
export const ADS_CONVERSIONS: Record<string, string | null> = {
  helpRequest: null,
  contactSubmission: null,
};

type Gtag = (
  command: "event",
  eventName: string,
  params: Record<string, unknown>,
) => void;

/** Fire a Google Ads conversion if one has been configured for this action. */
export function trackAdsConversion(action: keyof typeof ADS_CONVERSIONS): void {
  const sendTo = ADS_CONVERSIONS[action];
  if (!sendTo) return;

  const gtag = (window as unknown as { gtag?: Gtag }).gtag;
  if (typeof gtag !== "function") return;

  gtag("event", "conversion", { send_to: sendTo });
}
