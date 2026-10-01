import { useState } from "react";
import { Helmet } from "react-helmet-async";
import { Phone, CheckCircle2, Printer } from "lucide-react";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { HoneypotField } from "@/components/HoneypotField";
import { submitHelpRequest, submissionErrorMessage } from "@/lib/forms";
import { PRIMARY_PHONE, SITE, trackAdsConversion } from "@/lib/site";

const DOCUMENTS = [
  { id: "birth", label: "Birth certificate" },
  { id: "id", label: "State ID or driver's license" },
  { id: "ssc", label: "Social Security card" },
  { id: "dd214", label: "DD-214 (military discharge)" },
  { id: "other", label: "Something else" },
] as const;

/**
 * Fees, waivers, and timelines verified October 2026 against the issuing
 * agencies: PA Department of Health (vital records), PennDOT, SSA, and NPRC.
 * Re-check before relying on these in advertising — agencies change them
 * without notice, and the waiver rules in particular are what people act on.
 */
const COVERAGE = [
  {
    doc: "Certified birth certificate (PA)",
    cost: "$20",
    waiver:
      "Waived in full if you're experiencing homelessness — but the form needs an advocate to sign for you. That's where we come in.",
  },
  {
    doc: "Replacement Social Security card",
    cost: "Always free",
    waiver:
      "No fee, ever. Limited to 3 replacements a year and 10 in a lifetime, with hardship exceptions.",
  },
  {
    doc: "Pennsylvania photo ID",
    cost: "$43.50",
    waiver:
      "Free under Act 131 of 2020 if you're experiencing homelessness. You apply in person on form DL-54H and need a letter confirming your address.",
  },
  {
    doc: "REAL ID photo ID",
    cost: "$61.50",
    waiver:
      "The $30 REAL ID surcharge is one time. If you don't need to fly or enter a federal building, the standard ID is enough.",
  },
  {
    doc: "DD-214 military discharge",
    cost: "Always free",
    waiver:
      "No fee from the National Personnel Records Center. We'll file the request with you.",
  },
];

/** The paperwork barrier this page exists to remove. */
const ADVOCATES = [
  "A director of a facility where you're living or receiving services",
  "A social worker helping you get government services",
  "An attorney representing you",
];

const TRUST = [
  {
    heading: "We never hold your originals",
    body: "Everything we order is issued in your name and goes to you. Nothing gets stored with us that you can't get to.",
  },
  {
    heading: "No screening",
    body: "No income check, no proof of hardship, no program to enroll in. You need a document, we help.",
  },
  {
    heading: "A real nonprofit",
    body: `${SITE.legalName} is a 501(c)(3) public charity registered in Pennsylvania. EIN ${SITE.ein}.`,
  },
];

type Status = "idle" | "sending" | "sent" | "error";

const emptyForm = {
  name: "",
  phone: "",
  email: "",
  county: "",
  housingSituation: "",
  documents: [] as string[],
  documentsOther: "",
  deadline: "",
  veteran: false,
  notes: "",
};

const GetHelp = () => {
  const [form, setForm] = useState(emptyForm);
  const [honeypot, setHoneypot] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const update = <K extends keyof typeof emptyForm>(
    key: K,
    value: (typeof emptyForm)[K],
  ) => setForm((prev) => ({ ...prev, [key]: value }));

  const toggleDoc = (id: string) =>
    setForm((prev) => ({
      ...prev,
      documents: prev.documents.includes(id)
        ? prev.documents.filter((d) => d !== id)
        : [...prev.documents, id],
    }));

  const canSubmit =
    form.name.trim() !== "" &&
    (form.phone.trim() !== "" || form.email.trim() !== "") &&
    form.documents.length > 0;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit || status === "sending") return;

    setStatus("sending");
    setErrorMessage("");

    try {
      await submitHelpRequest({ ...form, honeypot });
      trackAdsConversion("helpRequest");
      setStatus("sent");
    } catch (error) {
      setErrorMessage(submissionErrorMessage(error));
      setStatus("error");
    }
  };

  const seo = (
    <Helmet>
      <title>Free Birth Certificate & ID Help in PA | We Sign For You | Klear Path</title>
      <meta
        name="description"
        content="Pennsylvania waives birth certificate and photo ID fees for people experiencing homelessness, but the forms need an organization to sign. Klear Path is that organization — and we pay the fee where there's no waiver."
      />
      <meta
        name="keywords"
        content="free birth certificate PA homeless, birth certificate fee waiver Pennsylvania advocate signature, free photo ID DL-54H Act 131, replace lost ID Pennsylvania, replacement Social Security card help, DD-214 replacement"
      />
      <link rel="canonical" href={`${SITE.url}/get-help`} />
    </Helmet>
  );

  if (status === "sent") {
    return (
      <Layout>
        {seo}
        <section className="py-20 lg:py-28">
          <div className="container-wide section-padding">
            <div className="max-w-xl rounded-2xl bg-card border border-border p-8 shadow-medium sm:p-12">
              <div className="flex items-center gap-2 text-primary mb-4">
                <CheckCircle2 className="h-5 w-5" aria-hidden="true" />
                <p className="text-xs font-semibold uppercase tracking-[0.18em]">
                  Request received
                </p>
              </div>
              <h1 className="font-serif text-3xl lg:text-4xl font-semibold leading-tight text-foreground">
                We got it. Someone will reach out within two business days.
              </h1>
              <p className="mt-5 text-lg leading-relaxed text-muted-foreground">
                If your deadline is sooner than that, call us instead — don't wait on
                the form.
              </p>
              <Button asChild size="lg" className="mt-6 w-full sm:w-auto">
                <a href={`tel:${PRIMARY_PHONE.href}`} data-cta="get-help-confirmation-call">
                  <Phone className="h-4 w-4" aria-hidden="true" />
                  Call {PRIMARY_PHONE.display}
                </a>
              </Button>
            </div>
          </div>
        </section>
      </Layout>
    );
  }

  return (
    <Layout>
      {seo}

      {/* Hero */}
      <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
        <div className="container-wide section-padding">
          <div className="max-w-3xl">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary-foreground/70">
              Free help · Pennsylvania
            </p>
            <h1 className="mt-5 text-4xl lg:text-5xl font-serif font-bold leading-tight text-balance">
              Your birth certificate and ID can be replaced for free. You just need
              someone to sign for you.
            </h1>
            <p className="mt-6 max-w-2xl text-xl text-primary-foreground/90 leading-relaxed">
              Pennsylvania already waives these fees for people experiencing
              homelessness. Almost nobody uses the waivers, because the forms require a
              nonprofit, a social worker, or an attorney to vouch for you — and if you're
              sleeping in your car, you don't have one. That's the gap we close. Where
              there's no waiver, we pay the fee.
            </p>

            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Button asChild size="lg" variant="secondary">
                <a href={`tel:${PRIMARY_PHONE.href}`} data-cta="get-help-hero-call">
                  <Phone className="h-4 w-4" aria-hidden="true" />
                  Call {PRIMARY_PHONE.display}
                </a>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="bg-transparent border-primary-foreground/40 text-primary-foreground hover:bg-primary-foreground/10 hover:text-primary-foreground"
              >
                <a href="#request" data-cta="get-help-hero-form">
                  Fill out the form
                </a>
              </Button>
            </div>

            <ul className="mt-10 grid gap-x-8 gap-y-2 text-primary-foreground/80 sm:grid-cols-2">
              <li>No cost to you</li>
              <li>No income requirement</li>
              <li>We sign the forms that need an organization</li>
              <li>You keep every document</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Why */}
      <section className="py-16 lg:py-24 bg-secondary border-b border-border">
        <div className="container-wide section-padding">
          <div className="max-w-3xl">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground">
              Why we do this
            </h2>
            <div className="mt-6 space-y-5 text-lg leading-relaxed text-muted-foreground">
              <p>
                Klear Path was started by someone who lost a housing placement twice
                over paperwork. The first time, the documents were turned in and
                logged, then disappeared. The second time, they were sitting in a
                manager's office — correct and complete — but that manager was on
                vacation and no one else had a key. The housing meeting went ahead
                without them. Both times, the wait started over from the bottom.
              </p>
              <p className="font-medium text-foreground">
                A second certified copy costs about twenty dollars. That's the only
                thing standing between those two outcomes — and twenty dollars is
                exactly what someone in that situation doesn't have.
              </p>
              <p>
                Here's the part we didn't learn until much later. Our founder spent a
                stretch sleeping in a tent in the woods, and had no idea any of this was
                free. Not the birth certificate fee waiver. Not the free PennDOT ID. Not
                the fact that an organization could sign the form and unlock both. He was
                paying attention, he was in the middle of it, and nobody ever told him.
              </p>
              <p>
                If he didn't know, most people don't. So this page says it plainly, in one
                place: the waivers exist, here's exactly what they require, and we'll be
                the organization that signs. Where there's no waiver, we pay.
              </p>
              <p>
                You keep your copy. When an office loses theirs or can't get to it, yours
                still works.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* The advocate gap */}
      <section className="py-16 lg:py-24 border-b border-border">
        <div className="container-wide section-padding">
          <div className="max-w-3xl">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground">
              Why the waivers go unused
            </h2>
            <div className="mt-6 space-y-5 text-lg leading-relaxed text-muted-foreground">
              <p>
                Pennsylvania waives the $20 birth certificate fee for anyone experiencing
                homelessness. It has for years. But the application has a second
                signature line, and it can only be signed by one of three people:
              </p>
            </div>

            <ul className="mt-6 space-y-3">
              {ADVOCATES.map((advocate) => (
                <li
                  key={advocate}
                  className="flex items-start gap-3 rounded-xl border border-border bg-card px-5 py-4"
                >
                  <CheckCircle2
                    className="mt-0.5 h-5 w-5 shrink-0 text-primary"
                    aria-hidden="true"
                  />
                  <span className="text-foreground">{advocate}</span>
                </li>
              ))}
            </ul>

            <div className="mt-6 space-y-5 text-lg leading-relaxed text-muted-foreground">
              <p>
                That person has to attest to who you are and that you're experiencing
                homelessness, and send a copy of their own photo ID with the form. If you
                don't already have a caseworker or a lawyer, the waiver may as well not
                exist. The fee was never really the barrier — the signature was.
              </p>
              <p className="font-medium text-foreground">
                That's the gap we exist to close. We're a 501(c)(3) that provides these
                services, so where we can sign for you, we sign. Where the form needs
                someone else — the shelter you're actually staying at, a caseworker, a
                lawyer — we know who to ask, and we make that call with you instead of
                handing you a phone number.
              </p>
              <p>
                Either way, you are not doing this alone and you are not paying. Ask, and
                we'll fill out our half, attach what the state needs, and tell you exactly
                where to take it.
              </p>
            </div>

            <div className="mt-8 rounded-2xl border border-border bg-secondary p-6">
              <h3 className="font-serif text-lg font-semibold text-foreground">
                They also unlock each other, in this order
              </h3>
              <ol className="mt-4 space-y-3 text-muted-foreground">
                <li>
                  <span className="font-medium text-foreground">1. Birth certificate.</span>{" "}
                  Proves who you are. Needed for almost everything else.
                </li>
                <li>
                  <span className="font-medium text-foreground">
                    2. Social Security card.
                  </span>{" "}
                  Always free, but SSA wants proof of identity first.
                </li>
                <li>
                  <span className="font-medium text-foreground">3. Photo ID.</span>{" "}
                  PennDOT asks for proof of identity, your Social Security card, and proof
                  of address — so it comes last.
                </li>
              </ol>
              <p className="mt-4 leading-relaxed text-muted-foreground">
                Start in the wrong place and you lose a day to a trip that was never going
                to work. If you're not sure where you stand, call us before you go
                anywhere.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Coverage */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="max-w-3xl">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground">
              What we cover
            </h2>
            <p className="mt-3 text-lg leading-relaxed text-muted-foreground">
              Either the fee gets waived and we sign for you, or there's no waiver and we
              pay it. Either way your cost is{" "}
              <span className="font-semibold text-primary">$0</span>.
            </p>

            <div className="mt-7 overflow-hidden rounded-2xl border border-border bg-card shadow-soft">
              <table className="w-full text-left">
                <thead className="border-b border-border bg-secondary text-xs uppercase tracking-wider text-muted-foreground">
                  <tr>
                    <th scope="col" className="px-5 py-3 font-semibold">
                      Document
                    </th>
                    <th scope="col" className="px-5 py-3 font-semibold">
                      Normal fee
                    </th>
                    <th
                      scope="col"
                      className="hidden px-5 py-3 font-semibold sm:table-cell"
                    >
                      How it becomes free
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border text-sm">
                  {COVERAGE.map((row) => (
                    <tr key={row.doc}>
                      <td className="px-5 py-4 align-top font-medium text-foreground">
                        {row.doc}
                        {/* The waiver note is the useful part, so keep it visible on
                            phones where the third column is hidden. */}
                        <span className="mt-1 block font-normal text-muted-foreground sm:hidden">
                          {row.waiver}
                        </span>
                      </td>
                      <td className="px-5 py-4 align-top text-muted-foreground">
                        {row.cost}
                      </td>
                      <td className="hidden px-5 py-4 align-top text-muted-foreground sm:table-cell">
                        {row.waiver}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <p className="mt-4 leading-relaxed text-muted-foreground">
              Fees, waivers, and processing times are set by the issuing agency and can
              change — we'll tell you what to expect when we talk. If you need something
              not listed here, ask anyway.
            </p>

            <div className="mt-6 rounded-2xl border border-primary/30 bg-accent p-6">
              <h3 className="font-serif text-lg font-semibold text-foreground">
                If you're experiencing homelessness, your PA photo ID is already free
              </h3>
              <p className="mt-2 leading-relaxed text-muted-foreground">
                Under Act 131 of 2020, PennDOT issues a free initial or renewal photo ID
                to Pennsylvanians experiencing homelessness. You apply in person at a
                Driver License Center, tell the counter staff you're requesting a free ID
                due to homeless status, and complete form DL-54H. For proof of address,
                PennDOT accepts a letter on letterhead from the shelter where you're
                staying or where you pick up mail.
              </p>
              <p className="mt-3 leading-relaxed text-muted-foreground">
                You'll still need proof of identity and your Social Security card to walk
                out with it — which is exactly what we help you get first. Tell us where
                you're staying and we'll work out who needs to write that letter and what
                else to bring, so you don't lose a day to a wasted trip.
              </p>
            </div>

            <div className="mt-6 space-y-2 text-sm leading-relaxed text-muted-foreground">
              <p>
                <span className="font-medium text-foreground">Birth certificates:</span>{" "}
                $20 for the first copy and $10 for each additional copy ordered at the
                same time, with the fee waived entirely for people experiencing
                homelessness. Ordering online through VitalChek adds a $10 service fee, so
                we usually order by mail or go in person. In-person requests made before
                2:30 p.m. at a Vital Records public office are filled the same day.
                Pennsylvania has a separate fee-waiver form for people who are in foster
                care or justice-involved — if that's you, say so and we'll use that one.
              </p>
              <p>
                <span className="font-medium text-foreground">
                  Social Security cards:
                </span>{" "}
                always free from SSA, but limited to 3 replacements per year and 10 in a
                lifetime. Name changes and corrections don't count against those limits,
                and SSA grants hardship exceptions if you have a letter from an employer
                or agency saying you need the physical card.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Form */}
      <section
        id="request"
        className="scroll-mt-24 py-16 lg:py-24 bg-secondary border-y border-border"
      >
        <div className="container-wide section-padding">
          <div className="max-w-2xl">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground">
              Tell us what you need
            </h2>
            <p className="mt-3 text-lg leading-relaxed text-muted-foreground">
              A few questions. We'll follow up within two business days.
            </p>

            <form
              onSubmit={handleSubmit}
              className="relative mt-8 space-y-6 rounded-2xl border border-border bg-card p-6 shadow-medium sm:p-8"
            >
              <HoneypotField id="get-help-website" value={honeypot} onChange={setHoneypot} />

              <div className="space-y-2">
                <Label htmlFor="name">Your name *</Label>
                <Input
                  id="name"
                  required
                  autoComplete="name"
                  value={form.name}
                  onChange={(e) => update("name", e.target.value)}
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone</Label>
                  <Input
                    id="phone"
                    type="tel"
                    inputMode="tel"
                    autoComplete="tel"
                    value={form.phone}
                    onChange={(e) => update("phone", e.target.value)}
                    aria-describedby="phone-hint"
                  />
                  <p id="phone-hint" className="text-xs text-muted-foreground">
                    Best way to reach you
                  </p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    inputMode="email"
                    autoComplete="email"
                    value={form.email}
                    onChange={(e) => update("email", e.target.value)}
                    aria-describedby="email-hint"
                  />
                  <p id="email-hint" className="text-xs text-muted-foreground">
                    Optional if you gave us a phone number
                  </p>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="county">County you're in</Label>
                <Input
                  id="county"
                  value={form.county}
                  onChange={(e) => update("county", e.target.value)}
                  placeholder="Montgomery, Bucks, Philadelphia…"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="housingSituation">Where are you staying right now?</Label>
                <Input
                  id="housingSituation"
                  value={form.housingSituation}
                  onChange={(e) => update("housingSituation", e.target.value)}
                  placeholder="A shelter, a friend's couch, my car, outside…"
                  aria-describedby="housing-hint"
                />
                <p id="housing-hint" className="text-xs text-muted-foreground">
                  Optional, and there's no wrong answer. It tells us which fee waiver you
                  qualify for and who needs to sign — nothing else.
                </p>
              </div>

              <fieldset>
                <legend className="text-sm font-medium text-foreground">
                  What do you need? *
                </legend>
                <p className="mt-1 text-xs text-muted-foreground">
                  Choose everything that applies.
                </p>
                <div className="mt-3 space-y-2">
                  {DOCUMENTS.map((doc) => {
                    const checked = form.documents.includes(doc.id);
                    return (
                      <label
                        key={doc.id}
                        htmlFor={`doc-${doc.id}`}
                        className={`flex cursor-pointer items-center gap-3 rounded-xl border px-4 py-3.5 transition-colors ${
                          checked
                            ? "border-primary bg-accent"
                            : "border-border bg-background hover:border-muted-foreground/40"
                        }`}
                      >
                        <Checkbox
                          id={`doc-${doc.id}`}
                          checked={checked}
                          onCheckedChange={() => toggleDoc(doc.id)}
                        />
                        <span className="text-foreground">{doc.label}</span>
                      </label>
                    );
                  })}
                </div>

                {form.documents.includes("other") && (
                  <div className="mt-3 space-y-2">
                    <Label htmlFor="documentsOther">What else do you need?</Label>
                    <Input
                      id="documentsOther"
                      value={form.documentsOther}
                      onChange={(e) => update("documentsOther", e.target.value)}
                      placeholder="e.g. marriage certificate, court records"
                    />
                  </div>
                )}
              </fieldset>

              <div className="space-y-2">
                <Label htmlFor="deadline">Is there a date you need it by?</Label>
                <Input
                  id="deadline"
                  value={form.deadline}
                  onChange={(e) => update("deadline", e.target.value)}
                  placeholder="e.g. housing appointment Aug 22"
                  aria-describedby="deadline-hint"
                />
                <p id="deadline-hint" className="text-xs text-muted-foreground">
                  A court date, housing meeting, job start — anything with a deadline
                </p>
              </div>

              <label
                htmlFor="veteran"
                className="flex cursor-pointer items-center gap-3 rounded-xl border border-border bg-background px-4 py-3.5"
              >
                <Checkbox
                  id="veteran"
                  checked={form.veteran}
                  onCheckedChange={(checked) => update("veteran", checked === true)}
                />
                <span className="text-foreground">I'm a veteran</span>
              </label>

              <div className="space-y-2">
                <Label htmlFor="notes">Anything else we should know?</Label>
                <Textarea
                  id="notes"
                  rows={3}
                  value={form.notes}
                  onChange={(e) => update("notes", e.target.value)}
                />
              </div>

              {status === "error" && (
                <p
                  role="alert"
                  className="rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive"
                >
                  {errorMessage} Call{" "}
                  <a href={`tel:${PRIMARY_PHONE.href}`} className="font-semibold underline">
                    {PRIMARY_PHONE.display}
                  </a>{" "}
                  or email{" "}
                  <a href={`mailto:${SITE.email}`} className="font-semibold underline">
                    {SITE.email}
                  </a>{" "}
                  and we'll take it from there.
                </p>
              )}

              <Button
                type="submit"
                size="lg"
                className="w-full"
                disabled={!canSubmit || status === "sending"}
                data-cta="get-help-submit"
              >
                {status === "sending" ? "Sending…" : "Send my request"}
              </Button>

              <p className="text-center text-sm text-muted-foreground">
                Rather talk to someone?{" "}
                <a
                  href={`tel:${PRIMARY_PHONE.href}`}
                  className="font-semibold text-primary underline"
                  data-cta="get-help-form-call"
                >
                  Call {PRIMARY_PHONE.display}
                </a>
              </p>
            </form>
          </div>
        </div>
      </section>

      {/* Pass it on — the awareness gap is the real barrier, so make the page
          easy to relay to someone who isn't reading it. */}
      <section className="py-16 lg:py-20 bg-primary text-primary-foreground">
        <div className="container-wide section-padding">
          <div className="max-w-3xl">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold">
              Know someone who needs this? Tell them.
            </h2>
            <p className="mt-4 text-lg leading-relaxed text-primary-foreground/90">
              Most people who qualify for these waivers have never heard of them. If
              you work at a shelter, a library, a church, a food pantry, a probation
              office, or an ER — or you just know someone sleeping rough — this is the
              whole message:
            </p>
            <blockquote className="mt-6 rounded-2xl border border-primary-foreground/25 bg-primary-foreground/10 p-6 text-lg leading-relaxed">
              Pennsylvania will replace your birth certificate and photo ID for free if
              you're experiencing homelessness. The forms need a nonprofit or social
              worker to sign. Klear Path does that, at no cost — {PRIMARY_PHONE.display}{" "}
              or klearpathhome.org/get-help.
            </blockquote>
            <p className="mt-6 text-primary-foreground/80">
              Caseworkers and outreach teams: call us directly. We'll take referrals by
              phone and handle the paperwork on our end.
            </p>

            <div className="mt-7 flex flex-col gap-3 sm:flex-row sm:items-center">
              <Button asChild size="lg" variant="secondary">
                <a
                  href="/klear-path-document-help.pdf"
                  target="_blank"
                  rel="noreferrer"
                  data-cta="get-help-flyer"
                >
                  <Printer className="h-4 w-4" aria-hidden="true" />
                  Print the one-page flyer
                </a>
              </Button>
              <p className="text-sm text-primary-foreground/70">
                One page, black and white, photocopies cleanly. Post it or hand it out —
                no permission needed.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Trust */}
      <section className="py-16 lg:py-20">
        <div className="container-wide section-padding">
          <div className="grid max-w-3xl gap-6 sm:grid-cols-3">
            {TRUST.map((item) => (
              <div key={item.heading}>
                <h3 className="font-serif text-lg font-semibold text-foreground">
                  {item.heading}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                  {item.body}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default GetHelp;
