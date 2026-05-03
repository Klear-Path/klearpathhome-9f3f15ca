import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { ArrowRight, Target, BarChart3, FileCheck, Repeat } from "lucide-react";

const tiers = [
  { amount: "$5,000", label: "Participant Readiness", desc: "Funds intake, onboarding, and individual readiness for one cohort participant." },
  { amount: "$10,000", label: "Workforce Training & Placement", desc: "Supports skill development, soft skills, and job placement pathways." },
  { amount: "$25,000", label: "Pilot Operations & Tracking", desc: "Underwrites case management, retention monitoring, and outcomes reporting." },
  { amount: "$50,000+", label: "Anchor a Pilot Site", desc: "Anchors deployment of a full pilot cohort with measurable, reportable outcomes." },
  { amount: "Custom", label: "Major Gift Opportunities", desc: "Naming, legacy, and multi-year structured giving available by conversation." },
];

const principles = [
  { icon: Target, title: "Outcome-Designed", desc: "Built around employment, retention, and housing stability milestones." },
  { icon: BarChart3, title: "Measurable", desc: "Participant tracking, employment data, and retention metrics from day one." },
  { icon: FileCheck, title: "Reportable", desc: "Funder-ready reporting aligned with foundation and government standards." },
  { icon: Repeat, title: "Replicable", desc: "Engineered as a pilot model that can scale to additional sites and counties." },
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
          <p className="text-xl text-primary-foreground/90 leading-relaxed mb-8">
            Klear Path is engineered around measurable outcomes, transparent reporting, and a replicable structure foundations and major donors can underwrite with confidence.
          </p>
          <Link to="/contact"><Button variant="hero" size="xl">Start a Funding Conversation<ArrowRight className="w-5 h-5" /></Button></Link>
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
          <Link to="/contact"><Button size="lg">Start a Funding Conversation<ArrowRight className="w-4 h-4" /></Button></Link>
          <Link to="/donate"><Button variant="outline" size="lg">Make a One-Time Gift</Button></Link>
        </div>
      </div>
    </section>

    <section className="py-16 lg:py-24 bg-secondary">
      <div className="container-wide section-padding">
        <div className="max-w-3xl mb-10">
          <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-4">Designed Around What Funders Need</h2>
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
      </div>
    </section>
  </Layout>
);

export default FundAPilot;