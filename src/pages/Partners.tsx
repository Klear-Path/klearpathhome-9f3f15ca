import { Link } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { MapPin, CheckCircle, Building2, FileText, Users, Shield, DollarSign, ArrowRight, Heart } from "lucide-react";

const Partners = () => {
  return (
    <Layout>
      {/* Hero */}
      <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
        <div className="container-wide section-padding">
          <div className="max-w-3xl">
            <p className="text-primary-foreground/70 font-medium mb-3 tracking-wide uppercase text-sm">
              Partnership Opportunity
            </p>
            <h1 className="text-4xl lg:text-5xl font-serif font-bold mb-6">
              Counties & Partners
            </h1>
            <p className="text-xl text-primary-foreground/90 leading-relaxed">
              We're seeking a land partner to help build Pennsylvania's first integrated 
              housing, safety, and workforce campus. Your support can transform how Bucks 
              and Montgomery Counties address homelessness.
            </p>
          </div>
        </div>
      </section>

      {/* The Ask */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="grid lg:grid-cols-2 gap-12 items-start">
            <div>
              <div className="w-16 h-16 rounded-xl bg-primary/10 flex items-center justify-center mb-6">
                <MapPin className="w-8 h-8 text-primary" />
              </div>
              <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
                Our Land Partnership Request
              </h2>
              <p className="text-lg text-muted-foreground leading-relaxed mb-6">
                To bring the Klear Path campus to life, we need approximately <strong>10 acres 
                of land</strong> in Bucks or Montgomery County. We're flexible on the arrangement 
                and open to creative solutions that work for both parties.
              </p>
              
              <div className="bg-accent rounded-xl p-6 mb-6">
                <h3 className="font-serif font-semibold text-lg mb-4">We're Open To:</h3>
                <ul className="space-y-3">
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                    <div>
                      <span className="font-medium text-foreground">Land Donation</span>
                      <p className="text-sm text-muted-foreground">Full tax benefits for charitable contribution</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                    <div>
                      <span className="font-medium text-foreground">Long-Term Ground Lease</span>
                      <p className="text-sm text-muted-foreground">Retain ownership while supporting the mission</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                    <div>
                      <span className="font-medium text-foreground">Public-Purpose Transfer</span>
                      <p className="text-sm text-muted-foreground">For county or municipal surplus property</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                    <div>
                      <span className="font-medium text-foreground">Hybrid Arrangements</span>
                      <p className="text-sm text-muted-foreground">Creative solutions tailored to your situation</p>
                    </div>
                  </li>
                </ul>
              </div>
            </div>

            <div className="bg-card rounded-2xl p-8 shadow-medium border border-border">
              <h3 className="font-serif text-2xl font-semibold mb-6">Ideal Site Characteristics</h3>
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <MapPin className="w-4 h-4 text-primary" />
                  </div>
                  <div>
                    <span className="font-medium">~10 Acres</span>
                    <p className="text-sm text-muted-foreground">Sufficient for Safety Center, micro-village, and training facilities</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <Building2 className="w-4 h-4 text-primary" />
                  </div>
                  <div>
                    <span className="font-medium">Accessible Location</span>
                    <p className="text-sm text-muted-foreground">Near public transit and essential services when possible</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <FileText className="w-4 h-4 text-primary" />
                  </div>
                  <div>
                    <span className="font-medium">Zoning Flexibility</span>
                    <p className="text-sm text-muted-foreground">We work with officials on necessary approvals</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <Shield className="w-4 h-4 text-primary" />
                  </div>
                  <div>
                    <span className="font-medium">Utilities Available</span>
                    <p className="text-sm text-muted-foreground">Or feasible connections to water, electric, and sewer</p>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="py-16 lg:py-24 bg-secondary">
        <div className="container-wide section-padding">
          <div className="text-center mb-12">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
              Benefits for Partner Communities
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              A Klear Path campus delivers measurable value to the host county and region.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
              <DollarSign className="w-10 h-10 text-primary mb-4" />
              <h3 className="font-serif font-semibold text-lg mb-2">Reduced Emergency Costs</h3>
              <p className="text-muted-foreground text-sm">
                Studies show integrated housing reduces ER visits, jail bookings, and 
                emergency shelter costs—saving counties significant resources.
              </p>
            </div>
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
              <Users className="w-10 h-10 text-primary mb-4" />
              <h3 className="font-serif font-semibold text-lg mb-2">Service Integration</h3>
              <p className="text-muted-foreground text-sm">
                We work alongside county social services, not in competition—strengthening 
                your existing continuum of care.
              </p>
            </div>
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
              <Shield className="w-10 h-10 text-primary mb-4" />
              <h3 className="font-serif font-semibold text-lg mb-2">Professional Management</h3>
              <p className="text-muted-foreground text-sm">
                24/7 staffing, security protocols, and community relations ensure the 
                campus is a good neighbor.
              </p>
            </div>
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
              <Building2 className="w-10 h-10 text-primary mb-4" />
              <h3 className="font-serif font-semibold text-lg mb-2">Full Compliance</h3>
              <p className="text-muted-foreground text-sm">
                We meet all local zoning, building codes, and safety requirements—no 
                exceptions or shortcuts.
              </p>
            </div>
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
              <FileText className="w-10 h-10 text-primary mb-4" />
              <h3 className="font-serif font-semibold text-lg mb-2">Transparent Reporting</h3>
              <p className="text-muted-foreground text-sm">
                Quarterly outcome reports and open financials so partners always know 
                the impact of their support.
              </p>
            </div>
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
              <Heart className="w-10 h-10 text-primary mb-4" />
              <h3 className="font-serif font-semibold text-lg mb-2">Community Goodwill</h3>
              <p className="text-muted-foreground text-sm">
                Be part of a landmark solution that demonstrates compassionate, 
                effective governance.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Compliance */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
                Our Compliance Commitment
              </h2>
              <p className="text-lg text-muted-foreground">
                We take regulatory compliance seriously. Partners can expect:
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-accent rounded-xl p-6">
                <h3 className="font-serif font-semibold text-lg mb-3">Building & Safety</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>Pennsylvania Building Code compliance</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>Fire safety and emergency planning</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>ADA accessibility requirements</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>Environmental impact considerations</span>
                  </li>
                </ul>
              </div>
              <div className="bg-accent rounded-xl p-6">
                <h3 className="font-serif font-semibold text-lg mb-3">Operations & Governance</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>Background-checked, trained staff</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>Written policies and resident agreements</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>Insurance and liability coverage</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>Regular coordination with local officials</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* PDF Download Placeholder */}
      <section className="py-16 lg:py-20 bg-primary text-primary-foreground">
        <div className="container-wide section-padding text-center">
          <h2 className="text-3xl lg:text-4xl font-serif font-semibold mb-4">
            Download Our Partnership Overview
          </h2>
          <p className="text-xl text-primary-foreground/90 max-w-2xl mx-auto mb-8">
            Get our one-page partnership overview to share with decision-makers.
          </p>
          
          {/* PDF Download Placeholder */}
          <div className="inline-block bg-primary-foreground/10 rounded-xl p-8 border border-primary-foreground/20">
            <FileText className="w-12 h-12 mx-auto mb-4 text-primary-foreground" />
            <p className="font-medium mb-2">Partnership Overview PDF</p>
            <p className="text-sm text-primary-foreground/70 mb-4">Coming Soon</p>
            <Button variant="hero" disabled>
              Download PDF
            </Button>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 lg:py-20">
        <div className="container-wide section-padding text-center">
          <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
            Let's Start a Conversation
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
            Whether you represent a county government, faith community, or are a private 
            landowner interested in social impact—we'd love to explore how we might work together.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/contact">
              <Button size="lg">
                Contact Us
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
            <Link to="/model">
              <Button variant="outline" size="lg">
                Learn About Our Model
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Partners;
