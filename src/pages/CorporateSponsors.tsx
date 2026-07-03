import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { ArrowRight, Building2, Briefcase, Cpu, Users, Target } from "lucide-react";

const pillars = [
  { icon: Target, title: "Sponsor a Pilot Component", desc: "Underwrite a specific stabilization, workforce, or infrastructure component of the pilot deployment." },
  { icon: Briefcase, title: "Support Workforce Readiness", desc: "Fund training, soft-skills development, transportation planning, and job-readiness supports." },
  { icon: Building2, title: "Become an Employer Partner", desc: "Open hiring pipelines that move participants from stabilization into retained employment." },
  { icon: Cpu, title: "Fund Technology and Tracking Infrastructure", desc: "Support the cloud-based data and reporting infrastructure that makes the model measurable." },
  { icon: Users, title: "Employee Giving and Volunteer Opportunities", desc: "Engage teams through matching gift programs, sponsorship campaigns, and skilled volunteering." },
];

const CorporateSponsors = () => (
  <Layout>
    <Helmet>
      <title>Corporate Partnerships & Sponsorship | Klear Path</title>
      <meta name="description" content="Klear Path works with businesses, employers, and corporate sponsors interested in supporting workforce reintegration, housing stability, and measurable community impact." />
      <meta name="keywords" content="corporate nonprofit sponsorship, workforce reintegration nonprofit, corporate social responsibility housing" />
      <link rel="canonical" href="https://klearpathhome.org/corporate-sponsors" />
    </Helmet>

    <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
      <div className="container-wide section-padding max-w-3xl">
        <p className="text-primary-foreground/70 font-medium mb-3 tracking-wide uppercase text-sm">Corporate Partnerships</p>
        <h1 className="text-4xl lg:text-5xl font-serif font-bold mb-6">Corporate Partnerships That Build Stability</h1>
        <p className="text-xl text-primary-foreground/90 leading-relaxed mb-8">
          Klear Path works with businesses, employers, and corporate sponsors interested in supporting workforce reintegration, housing stability, and measurable community impact.
        </p>
        <Link to="/contact"><Button variant="hero" size="xl" data-cta="corporate_sponsor_submit">Start a Corporate Partnership Conversation<ArrowRight className="w-5 h-5" /></Button></Link>
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
        <div className="mt-10 flex flex-wrap gap-3">
          <Link to="/contact"><Button size="lg" data-cta="corporate_sponsor_submit">Start a Conversation<ArrowRight className="w-4 h-4" /></Button></Link>
          <Link to="/employer-partners"><Button variant="outline" size="lg">Employer Partnerships</Button></Link>
          <Link to="/fund-a-pilot"><Button variant="outline" size="lg">Fund a Pilot</Button></Link>
        </div>
      </div>
    </section>
  </Layout>
);

export default CorporateSponsors;