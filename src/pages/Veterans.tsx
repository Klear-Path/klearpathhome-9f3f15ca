import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { ArrowRight, Shield, Briefcase, HeartHandshake, Handshake } from "lucide-react";

const sections = [
  { icon: Shield, title: "Stability Starts With Dignity", desc: "Every pathway begins with food, water, safety, and trust — not paperwork. Veterans facing instability are treated as people first, always." },
  { icon: Briefcase, title: "Rebuilding Through Work", desc: "Klear Path builds workforce reintegration pathways so participants can move from stabilization into meaningful employment and long-term retention." },
  { icon: HeartHandshake, title: "Support Beyond Emergency Aid", desc: "Temporary aid does not solve permanent problems. We build relationship-driven support that continues past the first crisis moment." },
  { icon: Handshake, title: "Partner With Klear Path to Support Veterans", desc: "Employers, funders, and community partners help us expand workforce pathways for veterans and former service members." },
];

const Veterans = () => (
  <Layout>
    <Helmet>
      <title>Support Veterans Facing Housing Instability | Klear Path</title>
      <meta name="description" content="Klear Path supports housing stability and workforce reintegration pathways for people experiencing instability, including veterans and former service members." />
      <meta name="keywords" content="veteran housing stability, veteran reintegration support, support veterans facing instability, workforce pathways for veterans" />
      <link rel="canonical" href="https://klearpathhome.org/veterans" />
    </Helmet>

    <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
      <div className="container-wide section-padding">
        <div className="max-w-3xl">
          <p className="text-primary-foreground/70 font-medium mb-3 tracking-wide uppercase text-sm">Veterans & Former Service Members</p>
          <h1 className="text-4xl lg:text-5xl font-serif font-bold mb-6">Support Veterans Facing Housing Instability</h1>
          <p className="text-xl text-primary-foreground/90 leading-relaxed mb-8">
            Klear Path supports housing stability and workforce reintegration pathways for people experiencing instability, including veterans and former service members.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link to="/donate"><Button variant="hero" size="xl" data-cta="veteran_support_click">Donate to Support Stability<ArrowRight className="w-5 h-5" /></Button></Link>
            <Link to="/contact"><Button variant="hero-outline" size="xl" data-cta="veteran_support_click">Partner With Us</Button></Link>
          </div>
          <p className="text-xs text-primary-foreground/60 mt-6 max-w-2xl">
            Klear Path is an independent 501(c)(3) nonprofit. We are not the U.S. Department of Veterans Affairs, do not administer VA benefits, and do not guarantee veteran housing benefits. Our programs complement — they do not replace — federal benefit systems.
          </p>
        </div>
      </div>
    </section>

    <section className="py-16 lg:py-24 bg-background">
      <div className="container-wide section-padding">
        <div className="grid md:grid-cols-2 gap-6">
          {sections.map((s) => (
            <div key={s.title} className="bg-card border border-border rounded-xl p-8">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <s.icon className="w-6 h-6 text-primary" />
              </div>
              <h2 className="font-serif text-xl font-semibold text-foreground mb-3">{s.title}</h2>
              <p className="text-muted-foreground leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>

    <section className="py-16 lg:py-24 bg-secondary">
      <div className="container-wide section-padding max-w-3xl mx-auto text-center">
        <h2 className="text-3xl font-serif font-bold text-foreground mb-4">Help Us Expand Workforce Pathways for Veterans</h2>
        <p className="text-lg text-muted-foreground mb-8">
          Explore the <Link to="/dignity-first-model" className="underline text-primary">Dignity-First Model</Link> or partner with us through <Link to="/employer-partners" className="underline text-primary">employer</Link>, <Link to="/corporate-sponsors" className="underline text-primary">corporate</Link>, or <Link to="/fund-a-pilot" className="underline text-primary">funding</Link> pathways.
        </p>
        <Link to="/donate"><Button size="xl" data-cta="veteran_support_click">Donate Today<ArrowRight className="w-5 h-5" /></Button></Link>
      </div>
    </section>
  </Layout>
);

export default Veterans;