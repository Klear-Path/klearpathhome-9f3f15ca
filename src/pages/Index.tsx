import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import {
  ArrowRight, Shield, Briefcase, TrendingUp, Heart, Building2, MapPin, Sun,
  FileText, BarChart3, Target, CheckCircle2, Handshake, Users, Landmark,
  Church, Cpu, Factory, GraduationCap, HeartHandshake, Coffee,
} from "lucide-react";

const Index = () => {
  return (
    <Layout>
      <Helmet>
        <title>Klear Path | Workforce-Driven Housing Stability</title>
        <meta name="description" content="Klear Path partners with counties, landowners, funders, and workforce organizations to create scalable housing stability programs that move individuals from crisis to employment, retention, and independence." />
        <meta name="keywords" content="workforce housing, housing stability programs, county housing partnerships, land donation nonprofit, pilot funding, homelessness prevention" />
        <script type="application/ld+json">{JSON.stringify({
          "@context": "https://schema.org",
          "@type": "NonprofitOrganization",
          "name": "Klear Path Home, Inc.",
          "url": "https://klearpathhome.org",
          "description": "A 501(c)(3) nonprofit building workforce-driven housing stability programs in Montgomery County, Bucks County, and the Pottstown regional service area.",
          "email": "erickmckee@klearpathhome.org",
          "taxID": "41-3156622",
          "nonprofitStatus": "501c3"
        })}</script>
      </Helmet>

      {/* HERO */}
      <section className="relative bg-primary text-primary-foreground overflow-hidden">
        <div className="container-wide section-padding py-20 lg:py-32">
          <div className="max-w-4xl animate-fade-in-up">
            <p className="text-primary-foreground/70 font-medium mb-5 tracking-wider uppercase text-xs">
              501(c)(3) Nonprofit · EIN 41-3156622
            </p>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-serif font-bold leading-[1.1] mb-6 text-balance">
              Workforce-Driven Housing Stability for Communities Ready to Build What Comes Next
            </h1>
            <p className="text-lg lg:text-xl text-primary-foreground/85 mb-10 max-w-3xl leading-relaxed">
              Klear Path partners with counties, municipalities, funders, landowners, and workforce
              organizations to create scalable housing stability programs that move individuals from
              crisis to employment, retention, and independence.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link to="/for-counties"><Button variant="hero" size="xl" data-cta="county_inquiry_submit"><Handshake className="w-5 h-5" />Partner With Us</Button></Link>
              <Link to="/fund-a-pilot"><Button variant="hero" size="xl" data-cta="fund_pilot_click"><Target className="w-5 h-5" />Fund a Pilot Site</Button></Link>
              <Link to="/land-partnerships"><Button variant="hero-outline" size="xl" data-cta="land_inquiry_submit"><MapPin className="w-5 h-5" />Donate Land or Property</Button></Link>
              <Link to="/donate"><Button variant="hero-outline" size="xl" data-cta="donation_click"><Heart className="w-5 h-5" />Support the Mission</Button></Link>
            </div>
          </div>
        </div>
        <div className="border-t border-primary-foreground/15">
          <div className="container-wide section-padding py-5 grid sm:grid-cols-3 gap-3 text-sm text-primary-foreground/80">
            <p><span className="font-semibold text-primary-foreground">Housing</span> is the stabilizer.</p>
            <p><span className="font-semibold text-primary-foreground">Employment</span> is the outcome.</p>
            <p><span className="font-semibold text-primary-foreground">Economic mobility</span> is the mission.</p>
          </div>
        </div>
      </section>

      {/* THE PROBLEM */}
      <section className="py-16 lg:py-24 bg-background">
        <div className="container-wide section-padding">
          <div className="max-w-4xl">
            <p className="text-primary font-medium mb-3 tracking-wide uppercase text-sm">The Problem</p>
            <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-6 text-balance">
              Fragmented Systems Create Cycles of Crisis
            </h2>
            <p className="text-lg text-muted-foreground leading-relaxed">
              Housing instability, unemployment, and disconnected support systems strain emergency
              services, public budgets, and local economies. Without coordinated stabilization,
              individuals cycle through shelters, ERs, and crisis systems—at significant public cost
              and minimal long-term outcome.
            </p>
          </div>
        </div>
      </section>

      {/* DAY ONE */}
      <section className="py-16 lg:py-20 bg-background border-b border-border">
        <div className="container-wide section-padding">
          <div className="grid lg:grid-cols-3 gap-8 items-center">
            <div className="lg:col-span-2">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Coffee className="w-6 h-6 text-primary" />
                </div>
                <p className="text-primary font-medium tracking-wide uppercase text-sm">Stability Starts on Day One</p>
              </div>
              <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-4">Before forms. Before systems. Before questions.</h2>
              <p className="text-lg text-muted-foreground leading-relaxed">
                Before forms, requirements, or systems, Klear Path begins with dignity: food, water, safety, trust, and a path forward. Dignity comes before paperwork — and every pathway starts on Day One.
              </p>
            </div>
            <div className="flex flex-col gap-3">
              <Link to="/donate"><Button size="lg" className="w-full" data-cta="donation_click">Support Day One Stability<ArrowRight className="w-4 h-4" /></Button></Link>
              <Link to="/dignity-first-model"><Button variant="outline" size="lg" className="w-full">Read the Dignity-First Model</Button></Link>
            </div>
          </div>
        </div>
      </section>

      {/* PARTNER PATHWAYS */}
      <section className="py-16 lg:py-24 bg-secondary">
        <div className="container-wide section-padding">
          <div className="max-w-3xl mb-10">
            <p className="text-primary font-medium mb-3 tracking-wide uppercase text-sm">Choose Your Pathway</p>
            <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-4">Every stakeholder has a role in stability.</h2>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {[
              { to: "/donate", icon: Heart, t: "Donate Today", d: "Fund dignity-first stabilization support.", cta: "donation_click" },
              { to: "/fund-a-pilot", icon: Target, t: "Fund a Pilot", d: "Underwrite a full workforce-driven pilot cohort.", cta: "fund_pilot_click" },
              { to: "/land-partnerships", icon: MapPin, t: "Donate Land or Property", d: "Turn idle parcels into launchpads for stability.", cta: "land_inquiry_submit" },
              { to: "/for-counties", icon: Landmark, t: "Partner as a County", d: "Deploy a scalable public-private pilot model.", cta: "county_inquiry_submit" },
              { to: "/employer-partners", icon: Briefcase, t: "Become an Employer Partner", d: "Open workforce pipelines from stabilization to retention.", cta: "employer_partner_submit" },
              { to: "/veterans", icon: Shield, t: "Support Veterans Facing Instability", d: "Back workforce reintegration pathways for veterans.", cta: "veteran_support_click" },
            ].map((c) => (
              <Link key={c.t} to={c.to} data-cta={c.cta} className="bg-card border border-border rounded-xl p-6 hover:shadow-medium transition-shadow">
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <c.icon className="w-6 h-6 text-primary" />
                </div>
                <h3 className="font-serif text-lg font-semibold text-foreground mb-2">{c.t}</h3>
                <p className="text-sm text-muted-foreground">{c.d}</p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* THE MODEL */}
      <section className="py-16 lg:py-24 bg-secondary">
        <div className="container-wide section-padding">
          <div className="max-w-3xl mb-12">
            <p className="text-primary font-medium mb-3 tracking-wide uppercase text-sm">The Klear Path Model</p>
            <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-4">
              Stabilize. Activate. Retain.
            </h2>
            <p className="text-lg text-muted-foreground">
              A workforce-first, three-phase framework engineered for measurable outcomes and replicable deployment.
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-6">
            {[
              { n: "01", icon: Shield, title: "Stabilize", desc: "Safe housing, intake, and readiness. Remove crisis barriers and establish a baseline for participation." },
              { n: "02", icon: Briefcase, title: "Activate", desc: "Workforce training, soft skills, and direct job placement through employer and partner pipelines." },
              { n: "03", icon: TrendingUp, title: "Retain", desc: "Employment support, retention tracking, and structured transition into independent housing." },
            ].map((p) => (
              <div key={p.n} className="bg-card rounded-xl border border-border p-8">
                <div className="flex items-center justify-between mb-5">
                  <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                    <p.icon className="w-6 h-6 text-primary" />
                  </div>
                  <span className="text-3xl font-serif font-bold text-primary/30">{p.n}</span>
                </div>
                <h3 className="text-xl font-serif font-semibold text-foreground mb-3">{p.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{p.desc}</p>
              </div>
            ))}
          </div>

          <div className="mt-10">
            <Link to="/housing-stabilization-model">
              <Button variant="outline" size="lg">View the Full Model<ArrowRight className="w-4 h-4" /></Button>
            </Link>
          </div>
        </div>
      </section>

      {/* WHY COUNTIES */}
      <section className="py-16 lg:py-24 bg-background">
        <div className="container-wide section-padding">
          <div className="max-w-3xl mb-12">
            <p className="text-primary font-medium mb-3 tracking-wide uppercase text-sm">For Counties & Municipalities</p>
            <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-4">
              Why Local Governments Partner With Klear Path
            </h2>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
            {[
              "Activates underused public and private land",
              "Reduces strain on shelters, ERs, and crisis systems",
              "Produces measurable employment and housing outcomes",
              "Strengthens regional workforce and economic stability",
              "Designed as a scalable, replicable pilot model",
              "Structured for public–private partnership alignment",
            ].map((b) => (
              <div key={b} className="flex items-start gap-3 bg-card border border-border rounded-xl p-5">
                <CheckCircle2 className="w-5 h-5 text-primary mt-1 flex-shrink-0" />
                <p className="text-foreground">{b}</p>
              </div>
            ))}
          </div>
          <div className="bg-accent rounded-2xl p-8 lg:p-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div>
              <h3 className="text-2xl font-serif font-semibold text-foreground mb-2">
                Have land, buildings, or underused property?
              </h3>
              <p className="text-muted-foreground">Let's turn it into a pathway home.</p>
            </div>
            <Link to="/for-counties"><Button size="lg">Explore County Partnership<ArrowRight className="w-4 h-4" /></Button></Link>
          </div>
        </div>
      </section>

      {/* LAND PARTNERSHIPS */}
      <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
        <div className="container-wide section-padding">
          <div className="max-w-3xl mb-12">
            <p className="text-primary-foreground/70 font-medium mb-3 tracking-wide uppercase text-sm">Land & Site Partnerships</p>
            <h2 className="text-3xl lg:text-4xl font-serif font-bold mb-4">
              Your Land Can Become a Launchpad for Generational Change
            </h2>
            <p className="text-lg text-primary-foreground/85 leading-relaxed">
              Klear Path is actively seeking land and site partnerships to deploy pilot stabilization housing.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-10">
            {[
              "Donated land",
              "Long-term land leases",
              "Underutilized municipal property",
              "Faith-based land partnerships",
              "Redevelopment parcels",
              "Public–private pilot sites",
            ].map((t) => (
              <div key={t} className="bg-primary-foreground/5 border border-primary-foreground/15 rounded-lg p-5">
                <p className="font-medium">{t}</p>
              </div>
            ))}
          </div>
          <Link to="/land-partnerships"><Button variant="hero" size="lg">View Land Partnership Options<ArrowRight className="w-4 h-4" /></Button></Link>
        </div>
      </section>

      {/* PROJECTED PILOT OUTCOMES */}
      <section className="py-16 lg:py-24 bg-background">
        <div className="container-wide section-padding">
          <div className="max-w-3xl mb-12">
            <p className="text-primary font-medium mb-3 tracking-wide uppercase text-sm">Projected Pilot Outcomes</p>
            <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-4">
              Designed Around Measurable Results
            </h2>
            <p className="text-lg text-muted-foreground">Targets for the initial pilot cohort.</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { n: "10–15", l: "Participants in the initial pilot cohort" },
              { n: "60–70%", l: "Employment placement target" },
              { n: "6+ mo", l: "Employment retention target" },
              { n: "↓", l: "Reduced reliance on emergency systems" },
            ].map((m) => (
              <div key={m.l} className="bg-card border border-border rounded-xl p-6">
                <p className="text-4xl font-serif font-bold text-primary mb-3">{m.n}</p>
                <p className="text-sm text-muted-foreground leading-relaxed">{m.l}</p>
              </div>
            ))}
          </div>
          <p className="text-sm text-muted-foreground mt-6 italic">Klear Path is in pilot/pre-launch development. Outcomes shown are targeted projections for the initial cohort.</p>
        </div>
      </section>

      {/* BUILT FOR FUNDERS */}
      <section className="py-16 lg:py-24 bg-secondary">
        <div className="container-wide section-padding">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <p className="text-primary font-medium mb-3 tracking-wide uppercase text-sm">Built for Funders</p>
              <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-6">
                Engineered for Outcomes, Reporting, and Scale
              </h2>
              <p className="text-lg text-muted-foreground leading-relaxed mb-6">
                Klear Path is structured around measurable outcomes, transparent reporting, and a
                replicable model—designed for foundations and major donors who fund evidence-based
                interventions.
              </p>
              <div className="flex flex-wrap gap-3">
                <Link to="/fund-a-pilot"><Button size="lg">Fund a Pilot<ArrowRight className="w-4 h-4" /></Button></Link>
                <Link to="/donate"><Button variant="outline" size="lg">Make a Gift</Button></Link>
              </div>
            </div>
            <div className="grid sm:grid-cols-2 gap-4">
              {[
                { icon: Users, t: "Participant Tracking" },
                { icon: Briefcase, t: "Employment Outcomes" },
                { icon: TrendingUp, t: "Retention Metrics" },
                { icon: Shield, t: "Housing Stability Milestones" },
                { icon: BarChart3, t: "Data-Driven Reporting" },
                { icon: FileText, t: "Funder-Ready Documentation" },
              ].map((c) => (
                <div key={c.t} className="bg-card border border-border rounded-xl p-5 flex items-start gap-3">
                  <c.icon className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                  <p className="font-medium text-foreground text-sm">{c.t}</p>
                </div>
              ))}
            </div>
          </div>
          <p className="text-center mt-12 text-xl font-serif text-foreground italic">
            "Fund a pilot. Prove the model. Scale the impact."
          </p>
        </div>
      </section>

      {/* POWERED BY THE SUN */}
      <section className="py-16 lg:py-24 bg-background">
        <div className="container-wide section-padding">
          <div className="max-w-4xl">
            <div className="flex items-center gap-3 mb-5">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <Sun className="w-6 h-6 text-primary" />
              </div>
              <p className="text-primary font-medium tracking-wide uppercase text-sm">Powered by the Sun</p>
            </div>
            <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-6">
              Solar-Ready Infrastructure for Long-Term Resilience
            </h2>
            <p className="text-lg text-muted-foreground leading-relaxed">
              Klear Path sites are designed for solar-ready infrastructure to reduce long-term
              operating costs, improve resilience, and lower the lifetime cost-per-participant of
              stabilization housing.
            </p>
          </div>
        </div>
      </section>

      {/* WHO WE SERVE */}
      <section className="py-16 lg:py-24 bg-secondary">
        <div className="container-wide section-padding">
          <div className="max-w-3xl">
            <p className="text-primary font-medium mb-3 tracking-wide uppercase text-sm">Who We Serve</p>
            <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-6">
              Adults Ready to Move From Instability to Independence
            </h2>
            <p className="text-lg text-muted-foreground leading-relaxed">
              Klear Path serves adults experiencing housing instability who face barriers to
              employment, stability, and long-term independence—and who are ready to engage in a
              structured pathway forward.
            </p>
          </div>
        </div>
      </section>

      {/* PARTNER ECOSYSTEM */}
      <section className="py-16 lg:py-24 bg-background">
        <div className="container-wide section-padding">
          <div className="max-w-3xl mb-12">
            <p className="text-primary font-medium mb-3 tracking-wide uppercase text-sm">Partner Ecosystem</p>
            <h2 className="text-3xl lg:text-4xl font-serif font-bold text-foreground mb-4">
              Built Through Coordinated Partnerships
            </h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { icon: Landmark, t: "Counties & Municipalities" },
              { icon: MapPin, t: "Landowners & Developers" },
              { icon: GraduationCap, t: "Workforce Organizations" },
              { icon: Factory, t: "Employers" },
              { icon: Building2, t: "Foundations" },
              { icon: Church, t: "Faith Communities" },
              { icon: HeartHandshake, t: "Service Providers" },
              { icon: Cpu, t: "Technology Partners" },
            ].map((p) => (
              <div key={p.t} className="bg-card border border-border rounded-xl p-5 text-center">
                <p.icon className="w-7 h-7 text-primary mx-auto mb-3" />
                <p className="text-sm font-medium text-foreground">{p.t}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* TAX EXEMPT */}
      <section className="py-12 lg:py-16 bg-secondary">
        <div className="container-wide section-padding">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-2xl lg:text-3xl font-serif font-bold text-foreground mb-4">Tax-Exempt Status</h2>
            <p className="text-muted-foreground leading-relaxed mb-2">
              Klear Path is an IRS-recognized 501(c)(3) public charity. Donations are tax-deductible to the fullest extent permitted by law.
            </p>
            <p className="text-sm font-semibold text-foreground mb-6">EIN: 41-3156622</p>
            <a href="/klearpath_501c3.pdf" target="_blank" rel="noopener noreferrer">
              <Button variant="outline" size="lg"><FileText className="w-4 h-4" />Download IRS Determination Letter</Button>
            </a>
          </div>
        </div>
      </section>

      {/* FINAL CTA */}
      <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
        <div className="container-wide section-padding text-center max-w-3xl mx-auto">
          <h2 className="text-3xl lg:text-4xl font-serif font-bold mb-6">Ready to Build What Comes Next?</h2>
          <p className="text-lg text-primary-foreground/85 mb-10 leading-relaxed">
            Whether you represent a county, hold land, fund initiatives, or want to support the mission directly—there is a place for you in this work.
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            <Link to="/contact"><Button variant="hero" size="xl"><Handshake className="w-5 h-5" />Start a Conversation</Button></Link>
            <Link to="/fund-a-pilot"><Button variant="hero-outline" size="xl"><Target className="w-5 h-5" />Fund a Pilot</Button></Link>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Index;