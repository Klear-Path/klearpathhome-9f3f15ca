import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { ArrowRight, Briefcase, TrendingUp, GraduationCap, Handshake } from "lucide-react";

const sections = [
  { icon: Briefcase, title: "Why Employer Partners Matter", desc: "Employment is the bridge that turns stabilization into independence. Employer partners make the model real." },
  { icon: GraduationCap, title: "Supported Workforce Pathways", desc: "We prepare participants through structured readiness, transportation planning, and documentation support." },
  { icon: Handshake, title: "Soft Skills and Readiness", desc: "Communication, workplace expectations, and job-site coaching are built into the pathway." },
  { icon: TrendingUp, title: "Retention Support", desc: "Klear Path stays engaged after placement to help participants reach 6+ month retention milestones." },
];

const EmployerPartners = () => (
  <Layout>
    <Helmet>
      <title>Employer Partners | Workforce Pathways | Klear Path</title>
      <meta name="description" content="Klear Path builds employer relationships that help participants move from stabilization into job readiness, employment placement, and long-term retention." />
      <meta name="keywords" content="employment after homelessness, workforce reintegration nonprofit, employer partnerships nonprofit" />
      <link rel="canonical" href="https://klearpathhome.org/employer-partners" />
    </Helmet>

    <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
      <div className="container-wide section-padding max-w-3xl">
        <p className="text-primary-foreground/70 font-medium mb-3 tracking-wide uppercase text-sm">Employer Partners</p>
        <h1 className="text-4xl lg:text-5xl font-serif font-bold mb-6">Employment Is the Bridge From Stability to Independence</h1>
        <p className="text-xl text-primary-foreground/90 leading-relaxed mb-8">
          Klear Path is building employer relationships that help participants move from stabilization into job readiness, employment placement, and long-term retention.
        </p>
        <Link to="/contact"><Button variant="hero" size="xl" data-cta="employer_partner_submit">Become an Employer Partner<ArrowRight className="w-5 h-5" /></Button></Link>
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
        <div className="mt-10 flex flex-wrap gap-3">
          <Link to="/contact"><Button size="lg" data-cta="employer_partner_submit">Become an Employer Partner<ArrowRight className="w-4 h-4" /></Button></Link>
          <Link to="/corporate-sponsors"><Button variant="outline" size="lg">Corporate Sponsorship</Button></Link>
        </div>
      </div>
    </section>
  </Layout>
);

export default EmployerPartners;