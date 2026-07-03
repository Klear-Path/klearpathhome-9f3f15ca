import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { ArrowRight, Coffee, ShieldCheck, HeartHandshake, Users, ClipboardX, Sunrise } from "lucide-react";

const pillars = [
  { icon: ClipboardX, title: "No Clipboards First", desc: "Trust cannot be built through intake forms. We meet people where they are before asking anything of them." },
  { icon: Users, title: "No Interrogation First", desc: "People in crisis have already been questioned by every system. We start with presence, not paperwork." },
  { icon: Coffee, title: "Food, Water, Safety, Trust", desc: "A meal, a drink, a safe moment. These are the first infrastructure investments in any pathway forward." },
  { icon: ShieldCheck, title: "Stability Before Systems", desc: "You cannot navigate a system while in survival mode. Stabilization comes before referrals." },
  { icon: HeartHandshake, title: "Relationship Before Requirements", desc: "Long-term outcomes are built on trusted relationships — not compliance checklists." },
  { icon: Sunrise, title: "Pathways After Trust", desc: "Once trust is established, workforce readiness, employment, and long-term independence become reachable." },
];

const DignityFirstModel = () => (
  <Layout>
    <Helmet>
      <title>Dignity Begins on Day One | The Klear Path Model</title>
      <meta name="description" content="Before clipboards, pressure, or paperwork, Klear Path starts with food, water, safety, trust, and a path forward. Learn how dignity-first support drives lasting stability." />
      <meta name="keywords" content="dignity-first support, day one stability, homelessness prevention support, housing stability programs" />
      <link rel="canonical" href="https://klearpathhome.org/dignity-first-model" />
    </Helmet>

    <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
      <div className="container-wide section-padding max-w-3xl">
        <p className="text-primary-foreground/70 font-medium mb-3 tracking-wide uppercase text-sm">The Dignity-First Model</p>
        <h1 className="text-4xl lg:text-5xl font-serif font-bold mb-6">Dignity Begins on Day One</h1>
        <p className="text-xl text-primary-foreground/90 leading-relaxed mb-8">
          Before clipboards, pressure, or paperwork, Klear Path starts with food, water, safety, trust, and a path forward.
        </p>
        <Link to="/donate"><Button variant="hero" size="xl" data-cta="donation_click">Support the Dignity-First Model<ArrowRight className="w-5 h-5" /></Button></Link>
      </div>
    </section>

    <section className="py-16 lg:py-24 bg-background">
      <div className="container-wide section-padding">
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {pillars.map((p) => (
            <div key={p.title} className="bg-card border border-border rounded-xl p-6">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <p.icon className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-serif text-lg font-semibold text-foreground mb-2">{p.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{p.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>

    <section className="py-16 lg:py-24 bg-secondary">
      <div className="container-wide section-padding max-w-3xl mx-auto">
        <h2 className="text-3xl font-serif font-bold text-foreground mb-6">Built From Lived Experience</h2>
        <p className="text-lg text-muted-foreground leading-relaxed mb-4">
          Klear Path's approach is built from lived experience. It recognizes that trust is often the first missing infrastructure in someone's life. The model starts by meeting immediate human needs, then builds toward employment, retention, and long-term independence.
        </p>
        <p className="text-lg text-muted-foreground leading-relaxed mb-8">
          Temporary aid does not solve permanent problems. Klear Path builds pathways, not dependency — and every pathway starts with dignity on Day One.
        </p>
        <div className="flex flex-wrap gap-3">
          <Link to="/donate"><Button size="lg" data-cta="donation_click">Donate Today<ArrowRight className="w-4 h-4" /></Button></Link>
          <Link to="/veterans"><Button variant="outline" size="lg">Support for Veterans</Button></Link>
          <Link to="/housing-stabilization-model"><Button variant="outline" size="lg">View the Full Model</Button></Link>
        </div>
      </div>
    </section>
  </Layout>
);

export default DignityFirstModel;