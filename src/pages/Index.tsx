import { Link } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Shield, Home, Briefcase, Users, ArrowRight, Heart, Building2, Leaf } from "lucide-react";
import heroImage from "@/assets/hero-community.jpg";

const Index = () => {
  return (
    <Layout>
      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${heroImage})` }}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-primary/95 via-primary/85 to-primary/70" />
        </div>
        
        <div className="relative container-wide section-padding py-20 lg:py-32">
          <div className="max-w-3xl animate-fade-in-up">
            <p className="text-primary-foreground/80 font-medium mb-4 tracking-wide uppercase text-sm">
              Serving Bucks & Montgomery Counties, Pennsylvania
            </p>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-serif font-bold text-primary-foreground leading-tight mb-6">
              A Clear Path from Crisis to Stability
            </h1>
            <p className="text-lg sm:text-xl text-primary-foreground/90 mb-8 max-w-2xl leading-relaxed">
              Klear Path is building Pennsylvania's first integrated housing, safety, and workforce 
              campus—designed with our neighbors experiencing homelessness, not just for them.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link to="/donate">
                <Button variant="hero" size="xl">
                  <Heart className="w-5 h-5" />
                  Donate Now
                </Button>
              </Link>
              <Link to="/partners">
                <Button variant="hero-outline" size="xl">
                  Partner With Us
                </Button>
              </Link>
              <Link to="/get-involved">
                <Button variant="hero-outline" size="xl">
                  Volunteer
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Mission Statement */}
      <section className="py-16 lg:py-24 bg-secondary">
        <div className="container-wide section-padding">
          <div className="max-w-4xl mx-auto text-center animate-fade-in">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-6">
              Dignity-First, Systems-Focused
            </h2>
            <p className="text-lg text-muted-foreground leading-relaxed">
              We believe every community member seeking stability deserves more than a bed—they 
              deserve a pathway to lasting independence. Our integrated model combines immediate 
              safety, dignified transitional housing, and workforce development into one 
              comprehensive campus designed to break the cycle of homelessness.
            </p>
          </div>
        </div>
      </section>

      {/* The Three Pillars */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="text-center mb-12 lg:mb-16">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
              Our Integrated Model
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Three interconnected programs working together to create lasting change.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 lg:gap-8">
            {/* 24/7 Safety Center */}
            <div className="bg-card rounded-xl p-6 lg:p-8 shadow-soft hover:shadow-medium transition-shadow border border-border">
              <div className="w-14 h-14 rounded-lg bg-primary/10 flex items-center justify-center mb-5">
                <Shield className="w-7 h-7 text-primary" />
              </div>
              <h3 className="text-xl font-serif font-semibold text-foreground mb-3">
                24/7 Safety Center
              </h3>
              <p className="text-muted-foreground leading-relaxed mb-4">
                A welcoming first point of contact offering immediate safety, warm meals, 
                showers, and connection to case management services—open around the clock.
              </p>
              <Link to="/model" className="inline-flex items-center gap-1 text-primary font-medium hover:gap-2 transition-all">
                Learn more <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

            {/* Micro-Village Housing */}
            <div className="bg-card rounded-xl p-6 lg:p-8 shadow-soft hover:shadow-medium transition-shadow border border-border">
              <div className="w-14 h-14 rounded-lg bg-primary/10 flex items-center justify-center mb-5">
                <Home className="w-7 h-7 text-primary" />
              </div>
              <h3 className="text-xl font-serif font-semibold text-foreground mb-3">
                Micro-Village Housing
              </h3>
              <p className="text-muted-foreground leading-relaxed mb-4">
                25 private, dignified pod-style units in Phase 1, providing transitional 
                housing where residents can rest, recover, and focus on their next steps.
              </p>
              <Link to="/model" className="inline-flex items-center gap-1 text-primary font-medium hover:gap-2 transition-all">
                Learn more <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

            {/* Workforce Pathway */}
            <div className="bg-card rounded-xl p-6 lg:p-8 shadow-soft hover:shadow-medium transition-shadow border border-border">
              <div className="w-14 h-14 rounded-lg bg-primary/10 flex items-center justify-center mb-5">
                <Briefcase className="w-7 h-7 text-primary" />
              </div>
              <h3 className="text-xl font-serif font-semibold text-foreground mb-3">
                Workforce & Skills Pathway
              </h3>
              <p className="text-muted-foreground leading-relaxed mb-4">
                Job training programs including solar installation and sustainability 
                skills—creating green-economy careers while residents build their futures.
              </p>
              <Link to="/model" className="inline-flex items-center gap-1 text-primary font-medium hover:gap-2 transition-all">
                Learn more <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Call for Partners */}
      <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
        <div className="container-wide section-padding">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <p className="text-primary-foreground/70 font-medium mb-3 tracking-wide uppercase text-sm">
                Partnership Opportunity
              </p>
              <h2 className="text-3xl lg:text-4xl font-serif font-semibold mb-6">
                We're Seeking a Land Partner
              </h2>
              <p className="text-primary-foreground/90 text-lg leading-relaxed mb-6">
                To build the Klear Path campus, we need approximately 10 acres of land in 
                Bucks or Montgomery County. We're open to donation, ground lease, or 
                public-purpose transfer arrangements.
              </p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-primary-foreground/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Building2 className="w-3.5 h-3.5" />
                  </div>
                  <span className="text-primary-foreground/90">County governments and municipal authorities</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-primary-foreground/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Users className="w-3.5 h-3.5" />
                  </div>
                  <span className="text-primary-foreground/90">Faith communities with available property</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-primary-foreground/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Leaf className="w-3.5 h-3.5" />
                  </div>
                  <span className="text-primary-foreground/90">Private landowners interested in social impact</span>
                </li>
              </ul>
              <Link to="/partners">
                <Button variant="hero" size="lg">
                  Explore Partnership Details
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            </div>
            <div className="bg-primary-light/30 rounded-2xl p-8 lg:p-10">
              <h3 className="font-serif text-2xl font-semibold mb-4">What We Bring</h3>
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-primary-foreground mt-2.5" />
                  <span>Full compliance with local zoning and building codes</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-primary-foreground mt-2.5" />
                  <span>Professional campus management and security</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-primary-foreground mt-2.5" />
                  <span>Reduction in emergency service costs for the county</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-primary-foreground mt-2.5" />
                  <span>Data-driven outcomes reporting and transparency</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-primary-foreground mt-2.5" />
                  <span>Integration with existing county social services</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Impact Preview */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="text-center mb-12">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
              Our Commitment to Transparency
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              We believe donors, partners, and community members deserve to see exactly 
              how their support creates change.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center p-6 bg-accent rounded-xl">
              <p className="text-4xl lg:text-5xl font-serif font-bold text-primary mb-2">25</p>
              <p className="text-muted-foreground">Housing pods (Phase 1)</p>
            </div>
            <div className="text-center p-6 bg-accent rounded-xl">
              <p className="text-4xl lg:text-5xl font-serif font-bold text-primary mb-2">24/7</p>
              <p className="text-muted-foreground">Safety Center access</p>
            </div>
            <div className="text-center p-6 bg-accent rounded-xl">
              <p className="text-4xl lg:text-5xl font-serif font-bold text-primary mb-2">100%</p>
              <p className="text-muted-foreground">Financial transparency</p>
            </div>
            <div className="text-center p-6 bg-accent rounded-xl">
              <p className="text-4xl lg:text-5xl font-serif font-bold text-primary mb-2">2</p>
              <p className="text-muted-foreground">Counties served</p>
            </div>
          </div>

          <div className="text-center mt-10">
            <Link to="/impact">
              <Button variant="outline" size="lg">
                View Full Impact Report
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 lg:py-20 bg-secondary">
        <div className="container-wide section-padding text-center">
          <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
            Ready to Make a Difference?
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
            Whether you donate, volunteer, or partner with us—every contribution helps 
            build pathways from crisis to stability for our neighbors.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/donate">
              <Button size="xl">
                <Heart className="w-5 h-5" />
                Donate Today
              </Button>
            </Link>
            <Link to="/get-involved">
              <Button variant="outline" size="xl">
                Get Involved
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Index;
