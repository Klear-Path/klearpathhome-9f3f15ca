import { useState } from "react";
import { Helmet } from "react-helmet-async";
import { Phone, CheckCircle2 } from "lucide-react";
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

const COVERAGE = [
  {
    doc: "Certified birth certificate (PA)",
    cost: "$20",
    time: "2–3 weeks by mail, same day in person",
  },
  {
    doc: "Replacement Social Security card",
    cost: "No fee",
    time: "About 2 weeks",
  },
  {
    doc: "Pennsylvania photo ID",
    cost: "Varies",
    time: "Same day at PennDOT",
  },
  {
    doc: "DD-214 military discharge",
    cost: "No fee",
    time: "2–6 weeks",
  },
];

const TRUST = [
  {
    heading: "We never hold your originals",
    body: "Everything we order is issued in your name and goes to you. Nothing gets stored with us that you can't get to.",
  },
  {
    heading: "No screening",
    body: "No income check, no proof of hardship, no program to enroll in. You need a document, we cover it.",
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
      <title>Get Help Replacing Your ID or Birth Certificate | Klear Path</title>
      <meta
        name="description"
        content="Klear Path pays the fee to replace a lost birth certificate, state ID, Social Security card, or DD-214 for Pennsylvania residents. Free, no income requirement, no screening."
      />
      <meta
        name="keywords"
        content="free birth certificate replacement PA, replace lost ID Pennsylvania, replacement Social Security card help, DD-214 replacement, vital records assistance"
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
              Lost your birth certificate, ID, or Social Security card? We'll pay to
              replace it.
            </h1>
            <p className="mt-6 max-w-2xl text-xl text-primary-foreground/90 leading-relaxed">
              A missing document shouldn't cost you a housing spot, a job, or a
              benefits appointment. We cover the fee and help you get a certified copy
              that stays in your hands.
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
              <li>You keep the document</li>
              <li>We never need your originals</li>
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
                So that's what we pay for. You keep your copy. When an office loses
                theirs or can't get to it, yours still works.
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
                      Typical wait
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border text-sm">
                  {COVERAGE.map((row) => (
                    <tr key={row.doc}>
                      <td className="px-5 py-4 font-medium text-foreground">
                        {row.doc}
                      </td>
                      <td className="px-5 py-4 text-muted-foreground">{row.cost}</td>
                      <td className="hidden px-5 py-4 text-muted-foreground sm:table-cell">
                        {row.time}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <p className="mt-4 leading-relaxed text-muted-foreground">
              Your cost is <span className="font-semibold text-primary">$0</span> for
              all of it. Fees and processing times are set by the issuing agency and
              can change — we'll tell you what to expect when we talk. If you need
              something not listed here, ask anyway.
            </p>
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
