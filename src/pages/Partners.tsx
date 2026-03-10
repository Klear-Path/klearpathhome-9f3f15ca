import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { CheckCircle, Building2, FileText, Users, Heart, ArrowRight, Handshake, DollarSign, Shield } from "lucide-react";

const Partners = () => {
  return (
    <Layout>
      <Helmet>
        <title>Partner With Klear Path | Community Housing Partnerships</title>
        <meta name="description" content="Partner with Klear Path to support innovative housing stabilization programs. We work with foundations, corporate sponsors, community organizations, and local governments." />
        <meta name="keywords" content="community housing partnerships, homelessness solutions nonprofit, housing stabilization programs, corporate social responsibility housing, foundation grants homelessness" />
      </Helmet>

      {/* Hero */}
      <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
        <div className="container-wide section-padding">
          <div className="max-w-3xl">
            <p className="text-primary-foreground/70 font-medium mb-3 tracking-wide uppercase text-sm">
              Collaboration Opportunities
            </p>
            <h1 className="text-4xl lg:text-5xl font-serif font-bold mb-6">
              Partner With Klear Path
            </h1>
            <p className="text-xl text-primary-foreground/90 leading-relaxed">
              We're building community housing partnerships that align resources, reduce fragmentation,
              and create scalable solutions for housing stability. Join us in making a measurable impact.
            </p>
          </div>
        </div>
      </section>

      {/* Partnership Types */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="text-center mb-12">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
              Collaboration Opportunities
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Klear Path works with a range of partners to expand the reach and impact of housing
              stabilization programs across our region.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-card rounded-xl p-8 shadow-soft border border-border">
              <Building2 className="w-10 h-10 text-primary mb-4" />
              <h3 className="font-serif font-semibold text-xl mb-3">Philanthropic Foundations</h3>
              <p className="text-muted-foreground mb-4">
                Foundation grants power our core programs and help us expand housing stabilization
                services. We welcome conversations about program funding, capacity building, and
                technology development grants.
              </p>
              <ul className="space-y-2">
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Program and operating support grants</span>
                </li>
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Technology and innovation funding</span>
                </li>
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Capacity building and scaling support</span>
                </li>
              </ul>
            </div>

            <div className="bg-card rounded-xl p-8 shadow-soft border border-border">
              <DollarSign className="w-10 h-10 text-primary mb-4" />
              <h3 className="font-serif font-semibold text-xl mb-3">Corporate Social Responsibility</h3>
              <p className="text-muted-foreground mb-4">
                Businesses can align their CSR goals with measurable housing stability outcomes.
                We offer structured partnership opportunities that benefit your team and our community.
              </p>
              <ul className="space-y-2">
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Employee volunteer engagement programs</span>
                </li>
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Matching gift and sponsorship programs</span>
                </li>
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>In-kind donations and professional services</span>
                </li>
              </ul>
            </div>

            <div className="bg-card rounded-xl p-8 shadow-soft border border-border">
              <Users className="w-10 h-10 text-primary mb-4" />
              <h3 className="font-serif font-semibold text-xl mb-3">Community Organizations</h3>
              <p className="text-muted-foreground mb-4">
                Local nonprofits, faith communities, and service providers can partner with Klear Path
                to coordinate referrals, share resources, and improve outcomes for shared clients.
              </p>
              <ul className="space-y-2">
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Service coordination and referral networks</span>
                </li>
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Joint programming and resource sharing</span>
                </li>
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Community outreach collaboration</span>
                </li>
              </ul>
            </div>

            <div className="bg-card rounded-xl p-8 shadow-soft border border-border">
              <Shield className="w-10 h-10 text-primary mb-4" />
              <h3 className="font-serif font-semibold text-xl mb-3">Housing Initiatives & Government</h3>
              <p className="text-muted-foreground mb-4">
                Local and county governments can partner with Klear Path to align homelessness prevention
                initiatives with community development goals and housing stability programs.
              </p>
              <ul className="space-y-2">
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Public-private partnership frameworks</span>
                </li>
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Data sharing and outcome tracking</span>
                </li>
                <li className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Land and resource alignment</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Why Partner */}
      <section className="py-16 lg:py-24 bg-secondary">
        <div className="container-wide section-padding">
          <div className="text-center mb-12">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
              Why Partner With Klear Path?
            </h2>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
              <h3 className="font-serif font-semibold text-lg mb-2">Innovative Model</h3>
              <p className="text-sm text-muted-foreground">
                We combine service coordination, community partnerships, and AI-assisted technology
                into a scalable approach to housing stabilization.
              </p>
            </div>
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
              <h3 className="font-serif font-semibold text-lg mb-2">Transparent Reporting</h3>
              <p className="text-sm text-muted-foreground">
                Partners receive regular impact reports, financial transparency, and clear
                communication about program outcomes.
              </p>
            </div>
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
              <h3 className="font-serif font-semibold text-lg mb-2">Scalable Impact</h3>
              <p className="text-sm text-muted-foreground">
                Your support helps build a replicable model that can expand to serve more communities
                experiencing housing instability.
              </p>
            </div>
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
              <h3 className="font-serif font-semibold text-lg mb-2">501(c)(3) Status</h3>
              <p className="text-sm text-muted-foreground">
                Klear Path Home, Inc. is a federally recognized public charity. Donations and grants
                are tax-deductible (EIN: 41-3156622).
              </p>
            </div>
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
              <h3 className="font-serif font-semibold text-lg mb-2">Community Rooted</h3>
              <p className="text-sm text-muted-foreground">
                Founded by individuals with lived experience and deep connections to Bucks and
                Montgomery Counties.
              </p>
            </div>
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
              <h3 className="font-serif font-semibold text-lg mb-2">Technology-Forward</h3>
              <p className="text-sm text-muted-foreground">
                AI-assisted tools help our small team maximize efficiency and generate better
                outcomes for every dollar invested.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Download & CTA */}
      <section className="py-16 lg:py-20 bg-primary text-primary-foreground">
        <div className="container-wide section-padding text-center">
          <Handshake className="w-12 h-12 mx-auto mb-4" />
          <h2 className="text-3xl lg:text-4xl font-serif font-semibold mb-4">
            Let's Explore a Partnership
          </h2>
          <p className="text-xl text-primary-foreground/90 max-w-2xl mx-auto mb-8">
            Contact us to discuss how your organization can support innovative housing
            stabilization programs and homelessness prevention initiatives.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/contact">
              <Button variant="hero" size="lg">
                Contact Us
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
            <a href="/KlearPath_Partnership_Overview.pdf" target="_blank" rel="noopener noreferrer">
              <Button variant="hero-outline" size="lg">
                <FileText className="w-4 h-4" />
                Download Partnership Overview
              </Button>
            </a>
          </div>
        </div>
      </section>

      {/* Learn About the Model */}
      <section className="py-16 lg:py-20">
        <div className="container-wide section-padding text-center">
          <h2 className="text-3xl font-serif font-semibold text-foreground mb-4">
            Learn About Our Model
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
            Understand the full housing stabilization framework and how our three-pillar approach
            creates lasting impact.
          </p>
          <Link to="/housing-stabilization-model">
            <Button variant="outline" size="lg">
              View Housing Stabilization Model
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>
    </Layout>
  );
};

export default Partners;
