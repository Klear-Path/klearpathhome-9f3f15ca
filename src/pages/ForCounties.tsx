import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Building2, ArrowRight, ShieldCheck, TrendingDown, Briefcase, Handshake, MapPin, BarChart3 } from "lucide-react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const benefits = [
  { icon: MapPin, title: "Activate Underused Land", desc: "Convert idle municipal, redevelopment, or surplus parcels into measurable public good." },
  { icon: TrendingDown, title: "Reduce Crisis System Burden", desc: "Lower repeat reliance on shelters, ERs, EMS, and the criminal justice system." },
  { icon: Briefcase, title: "Drive Employment Outcomes", desc: "Move participants into job training, placement, and 6+ month retention." },
  { icon: BarChart3, title: "Measurable, Reportable Impact", desc: "Outcome-tracked pilots produce data your council, board, or HUD report can cite." },
  { icon: Handshake, title: "Public–Private Partnership Structure", desc: "Designed to align with county human services, redevelopment authorities, and workforce boards." },
  { icon: ShieldCheck, title: "Scalable & Replicable", desc: "A pilot model built to expand across municipalities once outcomes are proven." },
];

const faqs = [
  {
    q: "What does Klear Path actually deliver to a county or municipality?",
    a: "A turnkey housing-stabilization pilot: site evaluation, participant intake, coordinated case management, workforce training pathways, employer placement, and quarterly outcome reporting that your board, council, or HUD CoC can cite directly.",
  },
  {
    q: "Who pays for the pilot?",
    a: "Klear Path pursues philanthropic, foundation, and state/federal funding to underwrite operations. County and municipal partners typically contribute land, surplus buildings, redevelopment alignment, or referrals through human-services agencies. We structure each agreement to minimize general-fund exposure.",
  },
  {
    q: "What kind of land or property is suitable?",
    a: "Underused municipal parcels of roughly 5–10 acres, surplus redevelopment authority properties, vacant institutional buildings, or sites already zoned for residential or mixed-use development. We perform a no-cost feasibility review for any candidate site.",
  },
  {
    q: "How long does it take to launch a pilot?",
    a: "Most pilots move from initial conversation to signed memorandum of understanding within 60–90 days, with on-site programming typically online within 6–12 months depending on site readiness and permitting.",
  },
  {
    q: "How is impact measured and reported?",
    a: "We track participant intake, length of stay, employment placement, 6-month retention, exits to permanent housing, and reductions in shelter, ER, and EMS utilization. Reports are delivered quarterly and formatted for council briefings, foundation reporting, and HUD CoC submission.",
  },
  {
    q: "Is Klear Path a 501(c)(3)?",
    a: "Yes. Klear Path Home, Inc. is a federally recognized 501(c)(3) public charity (EIN 41-3156622) headquartered at 410 Hopkins Ct, North Wales, PA 19454.",
  },
];

const ForCounties = () => (
  <Layout>
    <Helmet>
      <title>For Counties & Municipalities | Klear Path</title>
      <meta name="description" content="Klear Path helps local governments turn underused land into measurable housing, workforce, and economic mobility outcomes through scalable pilot deployment." />
      <script type="application/ld+json">
        {JSON.stringify({
          "@context": "https://schema.org",
          "@type": "FAQPage",
          mainEntity: faqs.map((f) => ({
            "@type": "Question",
            name: f.q,
            acceptedAnswer: { "@type": "Answer", text: f.a },
          })),
        })}
      </script>
    </Helmet>

    <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
      <div className="container-wide section-padding">
        <div className="max-w-3xl">
          <p className="text-primary-foreground/70 font-medium mb-3 tracking-wide uppercase text-sm">For Counties & Municipalities</p>
          <h1 className="text-4xl lg:text-5xl font-serif font-bold mb-6">Turn Idle Land Into Measurable Outcomes</h1>
          <p className="text-xl text-primary-foreground/90 leading-relaxed mb-8">
            Klear Path helps local governments convert underused land into housing, workforce, and economic mobility results—without expanding existing crisis systems.
          </p>
          <Link to="/contact">
            <Button variant="hero" size="xl">Start a Partnership Conversation<ArrowRight className="w-5 h-5" /></Button>
          </Link>
        </div>
      </div>
    </section>

    <section className="py-16 lg:py-24 bg-background">
      <div className="container-wide section-padding">
        <div className="max-w-3xl mb-12">
          <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-4">Why Counties Should Partner</h2>
          <p className="text-lg text-muted-foreground leading-relaxed">
            Designed for county commissioners, redevelopment authorities, housing departments, human services divisions, and municipal leadership.
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {benefits.map((b) => (
            <div key={b.title} className="bg-card border border-border rounded-xl p-6">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <b.icon className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-serif text-lg font-semibold text-foreground mb-2">{b.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{b.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>

    <section className="py-16 lg:py-24 bg-secondary">
      <div className="container-wide section-padding">
        <div className="max-w-4xl mx-auto bg-card border border-border rounded-2xl p-10 text-center">
          <Building2 className="w-12 h-12 text-primary mx-auto mb-4" />
          <h2 className="text-3xl font-serif font-bold text-foreground mb-4">Have Land, Buildings, or Underused Property?</h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Let's turn it into a pathway home. We work with counties to evaluate sites, structure agreements, and deploy a pilot designed to produce reportable outcomes.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/contact"><Button size="lg">Request a Site Evaluation<ArrowRight className="w-4 h-4" /></Button></Link>
            <Link to="/land-partnerships"><Button variant="outline" size="lg">View Land Partnership Options</Button></Link>
          </div>
        </div>
      </div>
    </section>

    <section className="py-16 lg:py-24 bg-background">
      <div className="container-wide section-padding max-w-3xl mx-auto">
        <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-4 text-center">
          Frequently Asked Questions
        </h2>
        <p className="text-lg text-muted-foreground mb-10 text-center">
          Answers for commissioners, redevelopment authorities, human services directors, and municipal staff.
        </p>
        <Accordion type="single" collapsible className="w-full">
          {faqs.map((f, i) => (
            <AccordionItem key={i} value={`item-${i}`}>
              <AccordionTrigger className="text-left text-base font-semibold">{f.q}</AccordionTrigger>
              <AccordionContent className="text-muted-foreground leading-relaxed">{f.a}</AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </section>
  </Layout>
);

export default ForCounties;