import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { ArrowRight, Target, BarChart3, FileCheck, Repeat } from "lucide-react";

const tiers = [
  { amount: "$5,000", label: "Participant Intake & Stabilization", desc: "Supports participant intake, onboarding, and stabilization supports." },
  { amount: "$10,000", label: "Workforce Readiness & Transportation", desc: "Supports workforce readiness, transportation planning, and employment preparation." },
  { amount: "$25,000", label: "Pilot Coordination & Reporting", desc: "Supports pilot coordination, participant tracking, and outcome reporting." },
  { amount: "$50,000+", label: "Anchor a Pilot Site", desc: "Anchors pilot development, operational infrastructure, and scalable deployment planning." },
  { amount: "Custom", label: "Major Gift Opportunities", desc: "Supports land, infrastructure, technology, or full pilot sponsorship conversations." },
];

const principles = [
  { icon: Target, title: "Measurable Outcomes", desc: "Employment, retention, and housing stability milestones built into every cohort." },
  { icon: BarChart3, title: "Transparent Reporting", desc: "Participant tracking, employment data, and retention metrics available to funders." },
  { icon: FileCheck, title: "Milestone Tracking", desc: "Participant milestones, employment placement, and retention tracked end-to-end." },
  { icon: Repeat, title: "Scalable Infrastructure", desc: "Cloud-supported data infrastructure engineered for replicable deployment." },
];

const FundAPilot = () => (
  <Layout>
    <Helmet>
      <title>Fund a Pilot | Foundation & Major Donor Giving | Klear Path</title>
      <meta name="description" content="Fund a Klear Path pilot and prove a scalable workforce-driven housing stabilization model. Designed for foundations and major donors." />
    </Helmet>

    <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
      <div className="container-wide section-padding">
        <div className="max-w-3xl">
          <p className="text-primary-foreground/70 font-medium mb-3 tracking-wide uppercase text-sm">Built for Funders</p>
          <h1 className="text-4xl lg:text-5xl font-serif font-bold mb-6">Fund a Pilot. Prove the Model. Scale the Impact.</h1>
          <p className="text-xl text-primary-foreground/90 leading-relaxed mb-4">
            Help launch a measurable workforce-centered housing stability pilot designed to move people from instability into employment, retention, and long-term independence.
          </p>
          <p className="text-lg text-primary-foreground/80 leading-relaxed mb-8 font-medium">
            Fund the infrastructure. Prove the model. Scale what works.
          </p>
          <Link to="/contact"><Button variant="hero" size="xl" data-cta="funding_inquiry_submit">Start a Funding Conversation<ArrowRight className="w-5 h-5" /></Button></Link>
        </div>
      </div>
    </section>

    <section className="py-16 lg:py-24 bg-background">
      <div className="container-wide section-padding">
        <div className="max-w-3xl mb-12">
          <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-4">Funding Levels</h2>
          <p className="text-lg text-muted-foreground">Tiered giving aligned with operational milestones.</p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tiers.map((t) => (
            <div key={t.amount} className="bg-card border border-border rounded-xl p-6">
              <p className="text-2xl font-serif font-bold text-primary mb-2">{t.amount}</p>
              <p className="font-semibold text-foreground mb-2">{t.label}</p>
              <p className="text-sm text-muted-foreground leading-relaxed">{t.desc}</p>
            </div>
          ))}
        </div>
        <div className="mt-10 flex flex-col sm:flex-row gap-4">
          <Link to="/contact"><Button size="lg" data-cta="funding_inquiry_submit">Start a Funding Conversation<ArrowRight className="w-4 h-4" /></Button></Link>
          <Link to="/donate"><Button variant="outline" size="lg" data-cta="donation_click">Make a One-Time Gift</Button></Link>
          <Link to="/land-partnerships"><Button variant="outline" size="lg">Land Partnerships</Button></Link>
          <Link to="/for-counties"><Button variant="outline" size="lg">County Partnerships</Button></Link>
        </div>
      </div>
    </section>

    <section className="py-16 lg:py-24 bg-secondary">
      <div className="container-wide section-padding">
        <div className="max-w-3xl mb-10">
          <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-4">Built for Accountability</h2>
          <p className="text-lg text-muted-foreground">Measurable, transparent, and reportable from Day One.</p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {principles.map((p) => (
            <div key={p.title} className="bg-card border border-border rounded-xl p-6">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <p.icon className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-serif font-semibold text-foreground mb-2">{p.title}</h3>
              <p className="text-sm text-muted-foreground">{p.desc}</p>
            </div>
          ))}
        </div>
        <div className="mt-10">
          <Link to="/impact"><Button variant="outline" size="lg">See Impact & Accountability<ArrowRight className="w-4 h-4" /></Button></Link>
        </div>
      </div>
    </section>
  </Layout>
);

export default FundAPilot;