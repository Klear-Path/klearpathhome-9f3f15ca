import { Link } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { BarChart3, Users, Home, Briefcase, FileText, Shield, DollarSign, ArrowRight, Heart, Eye } from "lucide-react";

const Impact = () => {
  return (
    <Layout>
      {/* Hero */}
      <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
        <div className="container-wide section-padding">
          <div className="max-w-3xl">
            <h1 className="text-4xl lg:text-5xl font-serif font-bold mb-6">
              Impact & Accountability
            </h1>
            <p className="text-xl text-primary-foreground/90 leading-relaxed">
              We believe donors, partners, and community members deserve complete transparency 
              about how their support creates change. Here's how we measure and report our impact.
            </p>
          </div>
        </div>
      </section>

      {/* Metrics Section */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="text-center mb-12">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
              Projected Impact Metrics
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              These are the outcomes we're designing for. As we launch, we'll update with 
              actual data and transparent reporting.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border text-center">
              <Home className="w-10 h-10 text-primary mx-auto mb-4" />
              <p className="text-4xl font-serif font-bold text-foreground mb-2">25</p>
              <p className="text-muted-foreground text-sm">Housing Units (Phase 1)</p>
            </div>
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border text-center">
              <Users className="w-10 h-10 text-primary mx-auto mb-4" />
              <p className="text-4xl font-serif font-bold text-foreground mb-2">500+</p>
              <p className="text-muted-foreground text-sm">Annual Safety Center Visits (Projected)</p>
            </div>
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border text-center">
              <Briefcase className="w-10 h-10 text-primary mx-auto mb-4" />
              <p className="text-4xl font-serif font-bold text-foreground mb-2">70%</p>
              <p className="text-muted-foreground text-sm">Job Placement Goal</p>
            </div>
            <div className="bg-card rounded-xl p-6 shadow-soft border border-border text-center">
              <BarChart3 className="w-10 h-10 text-primary mx-auto mb-4" />
              <p className="text-4xl font-serif font-bold text-foreground mb-2">80%</p>
              <p className="text-muted-foreground text-sm">Stable Housing Transition Goal</p>
            </div>
          </div>

          <div className="bg-accent rounded-xl p-6 lg:p-8 text-center">
            <p className="text-muted-foreground mb-4">
              <strong className="text-foreground">Data-Driven Approach:</strong> Once operational, 
              we'll publish quarterly outcome reports including demographics served, program 
              completion rates, housing placement data, and long-term stability tracking.
            </p>
            <p className="text-sm text-muted-foreground">
              All metrics will be independently verified and available to donors and partners upon request.
            </p>
          </div>
        </div>
      </section>

      {/* Financial Transparency */}
      <section className="py-16 lg:py-24 bg-secondary">
        <div className="container-wide section-padding">
          <div className="grid lg:grid-cols-2 gap-12 items-start">
            <div>
              <div className="w-16 h-16 rounded-xl bg-primary/10 flex items-center justify-center mb-6">
                <DollarSign className="w-8 h-8 text-primary" />
              </div>
              <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
                Financial Transparency
              </h2>
              <p className="text-lg text-muted-foreground leading-relaxed mb-6">
                Every dollar entrusted to Klear Path is handled with integrity. We maintain 
                clear separation between operating funds and restricted donations, and we 
                report openly on how funds are used.
              </p>
              
              <div className="space-y-4">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-lg bg-card flex items-center justify-center flex-shrink-0 shadow-soft">
                    <FileText className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">Annual Financial Reports</h3>
                    <p className="text-sm text-muted-foreground">
                      Published yearly with detailed breakdowns of revenue and expenses.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-lg bg-card flex items-center justify-center flex-shrink-0 shadow-soft">
                    <Eye className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">990 Form Availability</h3>
                    <p className="text-sm text-muted-foreground">
                      Our IRS Form 990 is available to any donor or partner upon request.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-lg bg-card flex items-center justify-center flex-shrink-0 shadow-soft">
                    <Shield className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">Fund Separation</h3>
                    <p className="text-sm text-muted-foreground">
                      Restricted donations are tracked separately and used only for designated purposes.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-card rounded-2xl p-8 shadow-medium border border-border">
              <h3 className="font-serif text-2xl font-semibold mb-6">Fund Categories</h3>
              
              <div className="space-y-6">
                <div className="border-b border-border pb-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium text-foreground">General Operating</span>
                    <span className="text-sm text-muted-foreground">Unrestricted</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Covers staff, utilities, maintenance, and day-to-day operations. Used where 
                    most needed to keep programs running.
                  </p>
                </div>
                
                <div className="border-b border-border pb-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium text-foreground">Capital Campaign</span>
                    <span className="text-sm text-muted-foreground">Restricted</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Designated for land acquisition, construction, and facility development.
                  </p>
                </div>
                
                <div className="border-b border-border pb-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium text-foreground">Program-Specific</span>
                    <span className="text-sm text-muted-foreground">Restricted</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Donations earmarked for workforce training, Safety Center operations, or 
                    housing support are used only for those purposes.
                  </p>
                </div>
                
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium text-foreground">Emergency Reserve</span>
                    <span className="text-sm text-muted-foreground">Board-Designated</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Prudent reserve for organizational stability and unexpected needs.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Policies & Governance */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
                Governance & Policies
              </h2>
              <p className="text-lg text-muted-foreground">
                Good governance protects our mission and your trust.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
                <h3 className="font-serif font-semibold text-lg mb-3">Board Oversight</h3>
                <p className="text-muted-foreground text-sm mb-4">
                  An independent Board of Directors provides strategic guidance and 
                  fiduciary oversight. Board members receive no compensation.
                </p>
                <Link to="/about" className="text-primary font-medium text-sm hover:underline">
                  Meet our leadership →
                </Link>
              </div>
              
              <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
                <h3 className="font-serif font-semibold text-lg mb-3">Conflict of Interest Policy</h3>
                <p className="text-muted-foreground text-sm mb-4">
                  All board members and key employees must disclose potential conflicts 
                  and recuse themselves from related decisions.
                </p>
                <span className="text-muted-foreground text-sm">Policy document available upon request</span>
              </div>
              
              <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
                <h3 className="font-serif font-semibold text-lg mb-3">Whistleblower Protection</h3>
                <p className="text-muted-foreground text-sm mb-4">
                  We maintain safe channels for reporting concerns about organizational 
                  conduct, with full protection against retaliation.
                </p>
                <span className="text-muted-foreground text-sm">Policy document available upon request</span>
              </div>
              
              <div className="bg-card rounded-xl p-6 shadow-soft border border-border">
                <h3 className="font-serif font-semibold text-lg mb-3">Document Retention</h3>
                <p className="text-muted-foreground text-sm mb-4">
                  Financial records, donor information, and program data are maintained 
                  according to IRS requirements and best practices.
                </p>
                <span className="text-muted-foreground text-sm">Policy document available upon request</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 lg:py-20 bg-primary text-primary-foreground">
        <div className="container-wide section-padding text-center">
          <h2 className="text-3xl lg:text-4xl font-serif font-semibold mb-4">
            Your Support, Our Accountability
          </h2>
          <p className="text-xl text-primary-foreground/90 max-w-2xl mx-auto mb-8">
            When you donate to Klear Path, you're supporting an organization committed to 
            transparency, measurable outcomes, and lasting change.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/donate">
              <Button variant="hero" size="lg">
                <Heart className="w-4 h-4" />
                Donate Now
              </Button>
            </Link>
            <Link to="/contact">
              <Button variant="hero-outline" size="lg">
                Request Financial Documents
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Impact;
